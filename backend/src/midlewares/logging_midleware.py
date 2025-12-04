from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from contextvars import ContextVar
import uuid
import time
import traceback
from typing import Dict, Any, Optional
from loguru import logger
import json

request_id_var: ContextVar[str] = ContextVar("request_id")


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        *,
        log_request_body: bool = True,
        log_response_body: bool = True,
        max_body_size: int = 1024,
        hide_sensitive_headers: list = None,
        include_traceback_in_logs: bool = False,
        traceback_frames_limit: int = 5,
    ):
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.max_body_size = max_body_size
        self.hide_sensitive_headers = hide_sensitive_headers or [
            "authorization",
            "cookie",
            "set-cookie",
            "proxy-authorization",
            "x-api-key",
        ]
        self.include_traceback_in_logs = include_traceback_in_logs
        self.traceback_frames_limit = traceback_frames_limit

    def _get_client_info(self, request: Request) -> Dict[str, Any]:
        """Извлекает информацию о клиенте"""
        if request.client:
            return {"host": request.client.host, "port": request.client.port}
        return {"host": None, "port": None}

    def _get_filtered_headers(self, request: Request) -> Dict[str, str]:
        """Фильтрует чувствительные заголовки"""
        headers = dict(request.headers)
        for sensitive in self.hide_sensitive_headers:
            sensitive_lower = sensitive.lower()
            for key in list(headers.keys()):
                if key.lower() == sensitive_lower and headers[key]:
                    headers[key] = "[FILTERED]"
        return headers

    async def _get_request_body(self, request: Request) -> Optional[str]:
        """Получает тело запроса для логирования"""
        if not self.log_request_body:
            return None

        try:
            body = await request.body()
            if body:
                body_str = body.decode("utf-8", errors="replace")
                if len(body_str) > self.max_body_size:
                    return f"{body_str[:self.max_body_size]}...[TRUNCATED {len(body_str)} chars]"
                return body_str
        except Exception:
            return "[UNABLE TO READ BODY]"
        return None

    def _get_error_context(self, exc: Exception) -> Dict[str, Any]:
        """Извлекает контекст ошибки для логирования"""
        error_info = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
        }

        if isinstance(exc, (ValueError, TypeError)):
            error_info["error_category"] = "validation_error"
        elif isinstance(exc, KeyError):
            error_info["error_category"] = "key_error"
        elif isinstance(exc, AttributeError):
            error_info["error_category"] = "attribute_error"
        else:
            error_info["error_category"] = "unhandled_exception"

        if self.include_traceback_in_logs:
            try:
                tb_lines = traceback.format_exception(type(exc), exc, exc.__traceback__)
                limited_tb = (
                    tb_lines[-self.traceback_frames_limit :]
                    if len(tb_lines) > self.traceback_frames_limit
                    else tb_lines
                )
                error_info["traceback"] = "".join(limited_tb)
            except:
                error_info["traceback"] = "[UNABLE TO EXTRACT TRACEBACK]"

        return error_info

    async def _get_response_body(self, response: Response) -> Optional[str]:
        """Получает тело ответа для логирования ошибок"""
        if not self.log_response_body:
            return None

        try:
            if hasattr(response, "body") and response.status_code >= 400:
                body = response.body
                if body:
                    body_str = body.decode("utf-8", errors="replace")
                    if len(body_str) > self.max_body_size:
                        return f"{body_str[:self.max_body_size]}...[TRUNCATED]"
                    return body_str
        except Exception:
            return "[UNABLE TO READ RESPONSE BODY]"
        return None

    def _format_log_data(self, **kwargs) -> str:
        """Форматирует данные для логирования в JSON-подобный вид"""
        filtered_data = {k: v for k, v in kwargs.items() if v is not None}

        try:
            for key, value in filtered_data.items():
                if hasattr(value, "__dict__"):
                    filtered_data[key] = str(value)
                elif isinstance(value, (dict, list)):
                    filtered_data[key] = value
        except:
            pass

        return json.dumps(filtered_data, ensure_ascii=False, default=str)

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:12]
        request_id_var.set(request_id)

        client_info = self._get_client_info(request)
        headers = self._get_filtered_headers(request)
        request_body = await self._get_request_body(request)

        logger.info(
            f"Request started - {self._format_log_data(
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                path=request.url.path,
                client_host=client_info['host'],
                body=request_body,
                query_params=dict(request.query_params)
            )}"
        )

        start_time = time.time()

        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            response_body = await self._get_response_body(response)

            if response.status_code >= 500:
                log_level = "error"
                log_msg = "Server error"
            elif response.status_code >= 400:
                log_level = "warning"
                log_msg = "Client error"
            else:
                log_level = "info"
                log_msg = "Request completed successfully"

            log_data = self._format_log_data(
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                process_time_ms=round(process_time * 1000, 2),
                response_size=response.headers.get("content-length"),
                response_body=response_body,
            )

            if log_level == "info":
                logger.info(f"{log_msg} - {log_data}")
            elif log_level == "warning":
                logger.warning(f"{log_msg} - {log_data}")
            else:
                logger.error(f"{log_msg} - {log_data}")

            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time-MS"] = str(round(process_time * 1000, 2))

            return response

        except Exception as exc:
            process_time = time.time() - start_time
            error_info = self._get_error_context(exc)

            log_data = self._format_log_data(
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                path=request.url.path,
                process_time_ms=round(process_time * 1000, 2),
                error_type=error_info["error_type"],
                error_message=error_info["error_message"],
                error_category=error_info.get("error_category"),
                client_host=client_info["host"],
                request_body=request_body,
                traceback=(
                    error_info.get("traceback")
                    if self.include_traceback_in_logs
                    else None
                ),
            )

            logger.error(f"Request failed with exception - {log_data}")

            error_response = {
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An internal server error occurred",
                    "request_id": request_id,
                }
            }

            return JSONResponse(
                status_code=500,
                content=error_response,
                headers={
                    "X-Request-ID": request_id,
                    "X-Process-Time-MS": str(round(process_time * 1000, 2)),
                },
            )

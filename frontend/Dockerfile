# ---------- Этап 1: сборка React-приложения ----------
FROM node:20-alpine AS build

WORKDIR /app

# Копируем package.json и package-lock.json из подпапки app
COPY app/package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем остальной код React-приложения
COPY app/ .

# Сборка продакшн версии
RUN npm run build

# ---------- Этап 2: деплой через Nginx ----------
FROM nginx:alpine

# Удаляем дефолтные файлы Nginx
RUN rm -rf /usr/share/nginx/html/*

# Копируем собранное приложение
COPY --from=build /app/build /usr/share/nginx/html

# Копируем кастомный nginx.conf
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
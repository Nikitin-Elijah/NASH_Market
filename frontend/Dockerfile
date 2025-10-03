FROM nginx:alpine

# Копирование всех frontend файлов
COPY . /usr/share/nginx/html/

# Создание директорий для статических файлов
RUN mkdir -p /usr/share/nginx/html/css \
    /usr/share/nginx/html/js \
    /usr/share/nginx/html/images

# Копирование конфигурации nginx (будет монтироваться через volumes)
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
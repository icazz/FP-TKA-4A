#!/bin/sh

# Replace placeholder with actual API_BASE env var (single quotes)
sed -i "s|REPLACE_API_BASE|'${API_BASE}'|g" /usr/share/nginx/html/index.html

exec nginx -g "daemon off;"
    
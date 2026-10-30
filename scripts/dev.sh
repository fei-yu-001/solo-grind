#!/usr/bin/env bash
# 一键起本地环境（MySQL / Redis 检查 + 后端 + 前端）
# 用法: bash scripts/dev.sh         起服务
#       bash scripts/dev.sh stop    停服务
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$ROOT/.logs"
mkdir -p "$LOG_DIR"

stop_all() {
  echo "== 停服务"
  for port in 8080 5173; do
    local pid
    pid=$(netstat -ano 2>/dev/null | grep ":$port .*LISTENING" | awk '{print $5}' | head -1)
    if [ -n "${pid:-}" ]; then
      taskkill //PID "$pid" //F >/dev/null 2>&1 && echo "  已停端口 $port (pid $pid)"
    else
      echo "  端口 $port 没有进程"
    fi
  done
}

if [ "${1:-}" = "stop" ]; then
  stop_all
  exit 0
fi

echo "== 1/4 检查 MySQL"
if mysql -uroot -pDDyu-996 -e "select 1" >/dev/null 2>&1; then
  echo "  MySQL 连接正常"
else
  echo "  MySQL 连不上，检查服务是否启动、密码是否 DDyu-996"
  exit 1
fi

if ! mysql -uroot -pDDyu-996 -e "use zhikao" >/dev/null 2>&1; then
  echo "  库 zhikao 不存在，先导入："
  echo "    mysql -uroot -pDDyu-996 --default-character-set=utf8mb4 < sql/schema.sql"
  echo "    mysql -uroot -pDDyu-996 --default-character-set=utf8mb4 < sql/data.sql"
  exit 1
fi
COUNT=$(mysql -uroot -pDDyu-996 -N -B -e "select count(*) from zhikao.question" 2>/dev/null)
echo "  库 zhikao 正常，题目 $COUNT 道"

echo "== 2/4 检查 Redis"
if command -v redis-cli >/dev/null 2>&1 && redis-cli ping >/dev/null 2>&1; then
  echo "  Redis 正常（$(redis-cli ping)）"
else
  echo "  Redis 没起，尝试启动 D:/ruangong/redis/redis-server.exe"
  if [ -x "/d/ruangong/redis/redis-server.exe" ]; then
    nohup bash -c "cd /d/ruangong/redis && exec ./redis-server.exe --port 6379" >"$LOG_DIR/redis.log" 2>&1 &
    disown
    sleep 3
    redis-cli ping >/dev/null 2>&1 && echo "  Redis 已启动" || { echo "  Redis 启动失败"; exit 1; }
  else
    echo "  找不到 redis-server，请手动启动"
    exit 1
  fi
fi

echo "== 3/4 启动后端（8080）"
if netstat -ano 2>/dev/null | grep -q ":8080 .*LISTENING"; then
  echo "  8080 已在监听，跳过"
else
  nohup bash -c "cd \"$ROOT/backend\" && exec mvn -B spring-boot:run" >"$LOG_DIR/backend.log" 2>&1 &
disown
  for _ in $(seq 1 60); do
    curl -s -o /dev/null --max-time 2 http://127.0.0.1:8080/api/auth/me && break
    sleep 2
  done
  if curl -s -o /dev/null --max-time 3 http://127.0.0.1:8080/api/auth/me; then
    echo "  后端起来了"
  else
    echo "  后端没起来，看 $LOG_DIR/backend.log"
    exit 1
  fi
fi

echo "== 4/4 启动前端（5173）"
if netstat -ano 2>/dev/null | grep -q ":5173 .*LISTENING"; then
  echo "  5173 已在监听，跳过"
else
  nohup bash -c "cd \"$ROOT/frontend\" && exec npm run dev" >"$LOG_DIR/frontend.log" 2>&1 &
disown
  for _ in $(seq 1 40); do
    curl -s -o /dev/null --max-time 2 http://127.0.0.1:5173/ && break
    sleep 1
  done
  echo "  前端起来了"
fi

echo
echo "打开 http://127.0.0.1:5173"
echo "  管理员 admin / admin123"
echo "  考生   student01 / student123"
echo "日志: $LOG_DIR/"
echo "停服务: bash scripts/dev.sh stop"

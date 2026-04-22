#!/bin/bash

echo "🚀 启动防火墙自动化运维平台"
echo "========================================"
echo ""

# 检查后端是否已在运行
if lsof -ti:8080 > /dev/null; then
    echo "⚠️  后端服务已在运行 (端口 8080)"
else
    echo "📦 启动后端服务..."
    source venv/bin/activate
    uvicorn main:app --host 0.0.0.0 --port 8080 &
    BACKEND_PID=$!
    echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"
fi

echo ""

# 检查前端是否已在运行
if lsof -ti:3000 > /dev/null; then
    echo "⚠️  前端服务已在运行 (端口 3000)"
else
    echo "📦 启动前端服务..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"
fi

echo ""
echo "========================================"
echo "🎉 服务启动完成！"
echo ""
echo "访问地址："
echo "  前端界面: http://localhost:3000"
echo "  后端 API:  http://localhost:8080"
echo "  API 文档:  http://localhost:8080/docs"
echo ""
echo "按 Ctrl+C 停止服务"
echo "========================================"

from local_git.data import DataManager
from local_git.table import TableManager
from local_git.namespaces import Namespaces
from local_git.db import TakocLocalDb
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
import os
import sys
from typing import Dict, Any, List

# 添加项目根目录到sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# 初始化配置和管理器
config_manager = TakocLocalDb()
namespace_manager = Namespaces(config_manager)
table_manager = TableManager(config_manager)
data_manager = DataManager(config_manager)

# 创建FastAPI应用
app = FastAPI(
    title="Takoc Local Git API",
    description="A RESTful API for managing namespaces, tables, and records in local Git storage",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc"
)

# 错误处理


@app.exception_handler(ValueError)
def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": {"code": "BAD_REQUEST", "message": str(exc)}}
    )


@app.exception_handler(FileNotFoundError)
def not_found_error_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": {"code": "NOT_FOUND", "message": str(exc)}}
    )

# 命名空间管理


@app.post("/namespace", status_code=201)
def create_namespace(namespace_data: Dict[str, Any]):
    try:
        name = namespace_data.get("name")
        description = namespace_data.get("description", "")
        if not name:
            raise ValueError("Namespace name is required")

        namespace = namespace_manager.create_namespace(name, description)
        # 添加id字段（使用name作为id）
        namespace["id"] = namespace["name"]
        return namespace
    except ValueError as e:
        if "already exists" in str(e):
            raise HTTPException(status_code=409, detail={
                                "error": {"code": "CONFLICT", "message": str(e)}})
        raise HTTPException(status_code=400, detail={
                            "error": {"code": "BAD_REQUEST", "message": str(e)}})


@app.get("/namespace")
def list_namespaces(page: int = 1, per_page: int = 20):
    try:
        namespaces = namespace_manager.list_namespaces()
        # 添加id字段
        for ns in namespaces:
            ns["id"] = ns["name"]

        # 分页
        total = len(namespaces)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_namespaces = namespaces[start:end]

        return {
            "total": total,
            "page": page,
            "per_page": per_page,
            "namespaces": paginated_namespaces
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={
                            "error": {"code": "INTERNAL_SERVER_ERROR", "message": str(e)}})


@app.get("/namespace/{namespace}")
def get_namespace(namespace: str):
    try:
        namespace_info = namespace_manager.get_namespace(namespace)
        # 添加id字段
        namespace_info["id"] = namespace_info["name"]
        return namespace_info
    except ValueError as e:
        raise HTTPException(status_code=404, detail={
                            "error": {"code": "NOT_FOUND", "message": str(e)}})


@app.put("/namespace/{namespace}")
def update_namespace(namespace: str, update_data: Dict[str, Any]):
    try:
        description = update_data.get("description")
        if description is None:
            raise ValueError("Description is required for update")

        namespace_info = namespace_manager.update_namespace(
            namespace, description)
        # 添加id字段
        namespace_info["id"] = namespace_info["name"]
        return namespace_info
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail={
                                "error": {"code": "NOT_FOUND", "message": str(e)}})
        raise HTTPException(status_code=400, detail={
                            "error": {"code": "BAD_REQUEST", "message": str(e)}})


@app.delete("/namespace/{namespace}", status_code=204)
def delete_namespace(namespace: str):
    try:
        namespace_manager.delete_namespace(namespace)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail={
                            "error": {"code": "NOT_FOUND", "message": str(e)}})

# 表管理


@app.post("/table/{namespace}", status_code=201)
def create_table(namespace: str, table_data: Dict[str, Any]):
    try:
        # 检查命名空间是否存在
        namespace_manager.get_namespace(namespace)

        name = table_data.get("name")
        description = table_data.get("description", "")
        schema = table_data.get("schema")

        if not name:
            raise ValueError("Table name is required")
        if not schema:
            raise ValueError("Table schema is required")

        table = table_manager.create_table(
            namespace, name, description, schema)
        # 添加id和namespace字段
        table["id"] = table["name"]
        table["namespace"] = namespace
        return table
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail={
                                "error": {"code": "NOT_FOUND", "message": str(e)}})
        if "already exists" in str(e):
            raise HTTPException(status_code=409, detail={
                                "error": {"code": "CONFLICT", "message": str(e)}})
        raise HTTPException(status_code=400, detail={
                            "error": {"code": "BAD_REQUEST", "message": str(e)}})


@app.get("/table/{namespace}")
def list_tables(namespace: str, page: int = 1, per_page: int = 20):
    try:
        # 检查命名空间是否存在
        namespace_manager.get_namespace(namespace)

        tables = table_manager.list_tables(namespace)
        # 添加id和namespace字段
        for table in tables:
            table["id"] = table["name"]
            table["namespace"] = namespace

        # 分页
        total = len(tables)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_tables = tables[start:end]

        return {
            "total": total,
            "page": page,
            "per_page": per_page,
            "tables": paginated_tables
        }
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail={
                                "error": {"code": "NOT_FOUND", "message": str(e)}})
        raise HTTPException(status_code=500, detail={
                            "error": {"code": "INTERNAL_SERVER_ERROR", "message": str(e)}})


@app.get("/table/{namespace}/{table}")
def get_table(namespace: str, table: str):
    try:
        table_info = table_manager.get_table(namespace, table)
        # 添加id和namespace字段
        table_info["id"] = table_info["name"]
        table_info["namespace"] = namespace
        return table_info
    except ValueError as e:
        raise HTTPException(status_code=404, detail={
                            "error": {"code": "NOT_FOUND", "message": str(e)}})


@app.put("/table/{namespace}/{table}")
def update_table(namespace: str, table: str, update_data: Dict[str, Any]):
    try:
        description = update_data.get("description")
        schema = update_data.get("schema")

        table_info = table_manager.update_table(
            namespace, table, description, schema)
        # 添加id和namespace字段
        table_info["id"] = table_info["name"]
        table_info["namespace"] = namespace
        return table_info
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail={
                                "error": {"code": "NOT_FOUND", "message": str(e)}})
        raise HTTPException(status_code=400, detail={
                            "error": {"code": "BAD_REQUEST", "message": str(e)}})


@app.delete("/table/{namespace}/{table}", status_code=204)
def delete_table(namespace: str, table: str):
    try:
        table_manager.delete_table(namespace, table)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail={
                            "error": {"code": "NOT_FOUND", "message": str(e)}})

# 数据操作


@app.post("/data/{namespace}/{table}", status_code=201)
def create_record(namespace: str, table: str, record_data: Dict[str, Any]):
    try:
        # 检查命名空间和表是否存在
        table_manager.get_table(namespace, table)

        record = data_manager.create_record(namespace, table, record_data)
        return record
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail={
                                "error": {"code": "NOT_FOUND", "message": str(e)}})
        raise HTTPException(status_code=400, detail={
                            "error": {"code": "BAD_REQUEST", "message": str(e)}})


@app.get("/data/{namespace}/{table}")
def list_records(namespace: str, table: str, page: int = 1, per_page: int = 20):
    try:
        # 检查命名空间和表是否存在
        table_manager.get_table(namespace, table)

        records = data_manager.list_records(namespace, table)

        # 分页
        total = len(records)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_records = records[start:end]

        return {
            "total": total,
            "page": page,
            "per_page": per_page,
            "records": paginated_records
        }
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail={
                                "error": {"code": "NOT_FOUND", "message": str(e)}})
        raise HTTPException(status_code=500, detail={
                            "error": {"code": "INTERNAL_SERVER_ERROR", "message": str(e)}})


@app.get("/data/{namespace}/{table}/{record_id}")
def get_record(namespace: str, table: str, record_id: str):
    try:
        record = data_manager.get_record(namespace, table, record_id)
        return record
    except ValueError as e:
        raise HTTPException(status_code=404, detail={
                            "error": {"code": "NOT_FOUND", "message": str(e)}})


@app.put("/data/{namespace}/{table}/{record_id}")
def update_record(namespace: str, table: str, record_id: str, update_data: Dict[str, Any]):
    try:
        data = update_data.get("data")
        if data is None:
            raise ValueError("Record data is required")

        record = data_manager.update_record(namespace, table, record_id, data)
        return record
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail={
                                "error": {"code": "NOT_FOUND", "message": str(e)}})
        raise HTTPException(status_code=400, detail={
                            "error": {"code": "BAD_REQUEST", "message": str(e)}})


@app.delete("/data/{namespace}/{table}/{record_id}", status_code=204)
def delete_record(namespace: str, table: str, record_id: str):
    try:
        data_manager.delete_record(namespace, table, record_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail={
                            "error": {"code": "NOT_FOUND", "message": str(e)}})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

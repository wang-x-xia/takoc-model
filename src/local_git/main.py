from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from .db import TakocLocalDb
from .namespaces import Namespaces

# Initialize configurations and managers
db = TakocLocalDb()
namespaces_manager = Namespaces(db)

# Create FastAPI application
app = FastAPI(
    title="Takoc Local Git API",
    description="A RESTful API for managing namespaces, tables, and records in local Git storage",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc"
)


# Error handling


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


# Namespace management


@app.post("/namespace", status_code=201)
def create_namespace(namespace_data: dict[str, Any]):
    try:
        name = namespace_data.get("name")
        description = namespace_data.get("description", "")
        if not name:
            raise ValueError("Namespace name is required")

        # 创建命名空间
        namespace = namespaces_manager.create_namespace(name, description)

        # 返回命名空间信息
        return {
            "id": name,
            "name": name,
            "description": description
        }
    except ValueError as e:
        if "already exists" in str(e):
            raise HTTPException(status_code=409, detail={
                "error": {"code": "CONFLICT", "message": str(e)}})
        raise HTTPException(status_code=400, detail={
            "error": {"code": "BAD_REQUEST", "message": str(e)}})


@app.get("/namespace")
def list_namespaces(page: int = 1, per_page: int = 20):
    try:
        namespaces = namespaces_manager.list_namespaces()

        # 格式化输出
        formatted_namespaces = []
        for ns in namespaces:
            formatted_namespaces.append({
                "id": ns.name,
                "name": ns.name,
                "description": ns.description
            })

        # 分页
        total = len(formatted_namespaces)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_namespaces = formatted_namespaces[start:end]

        return {
            "total": total,
            "page": page,
            "per_page": per_page,
            "namespaces": paginated_namespaces
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "error": {"code": "INTERNAL_SERVER_ERROR", "message": str(e)}})


@app.get("/namespace/{namespace_name}")
def get_namespace(namespace_name: str):
    try:
        # Get namespace
        namespace = namespaces_manager.get_namespace(namespace_name)

        # Get namespace metadata to retrieve description
        namespaces_data = namespaces_manager._load_namespaces()
        description = ""
        for ns in namespaces_data.namespaces:
            if ns.name == namespace_name:
                description = ns.description
                break

        # Return namespace information
        return {
            "id": namespace_name,
            "name": namespace_name,
            "description": description
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail={
            "error": {"code": "NOT_FOUND", "message": str(e)}})


@app.put("/namespace/{namespace_name}")
def update_namespace(namespace_name: str, update_data: dict[str, Any]):
    try:
        description = update_data.get("description")
        if description is None:
            raise ValueError("Description is required for update")

        # 更新命名空间
        namespaces_manager.update_namespace(namespace_name, description)

        # 返回更新后的命名空间信息
        return {
            "id": namespace_name,
            "name": namespace_name,
            "description": description
        }
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail={
                "error": {"code": "NOT_FOUND", "message": str(e)}})
        raise HTTPException(status_code=400, detail={
            "error": {"code": "BAD_REQUEST", "message": str(e)}})


@app.delete("/namespace/{namespace_name}", status_code=204)
def delete_namespace(namespace_name: str):
    try:
        namespaces_manager.delete_namespace(namespace_name)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail={
            "error": {"code": "NOT_FOUND", "message": str(e)}})


# Table management


@app.post("/table/{namespace_name}", status_code=201)
def create_table(namespace_name: str, table_data: dict[str, Any]):
    try:
        # 获取命名空间
        namespace = namespaces_manager.get_namespace(namespace_name)

        name = table_data.get("name")
        description = table_data.get("description", "")

        if not name:
            raise ValueError("Table name is required")

        # 创建表
        table = namespace.create_table(name, description)

        # 返回表信息
        return {
            "id": name,
            "name": name,
            "description": description,
            "namespace": namespace_name
        }
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail={
                "error": {"code": "NOT_FOUND", "message": str(e)}})
        if "already exists" in str(e):
            raise HTTPException(status_code=409, detail={
                "error": {"code": "CONFLICT", "message": str(e)}})
        raise HTTPException(status_code=400, detail={
            "error": {"code": "BAD_REQUEST", "message": str(e)}})


@app.get("/table/{namespace_name}")
def list_tables(namespace_name: str, page: int = 1, per_page: int = 20):
    try:
        # 获取命名空间
        namespace = namespaces_manager.get_namespace(namespace_name)

        # 获取表列表
        table_names = namespace.list_tables()

        # 格式化输出
        tables = []
        for table_name in table_names:
            tables.append({
                "id": table_name,
                "name": table_name,
                "namespace": namespace_name
            })

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


@app.get("/table/{namespace_name}/{table_name}")
def get_table(namespace_name: str, table_name: str):
    try:
        # 获取命名空间
        namespace = namespaces_manager.get_namespace(namespace_name)

        # 获取表
        table = namespace.get_table(table_name)

        # 返回表信息
        return {
            "id": table_name,
            "name": table_name,
            "namespace": namespace_name
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail={
            "error": {"code": "NOT_FOUND", "message": str(e)}})


@app.put("/table/{namespace_name}/{table_name}")
def update_table(namespace_name: str, table_name: str, update_data: dict[str, Any]):
    try:
        # 获取命名空间
        namespace = namespaces_manager.get_namespace(namespace_name)

        description = update_data.get("description")
        if description is None:
            raise ValueError("Description is required for update")

        # 更新表
        namespace.update_table(table_name, description)

        # 返回更新后的表信息
        return {
            "id": table_name,
            "name": table_name,
            "description": description,
            "namespace": namespace_name
        }
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail={
                "error": {"code": "NOT_FOUND", "message": str(e)}})
        raise HTTPException(status_code=400, detail={
            "error": {"code": "BAD_REQUEST", "message": str(e)}})


@app.delete("/table/{namespace_name}/{table_name}", status_code=204)
def delete_table(namespace_name: str, table_name: str):
    try:
        # 获取命名空间
        namespace = namespaces_manager.get_namespace(namespace_name)

        # 删除表
        namespace.delete_table(table_name)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail={
            "error": {"code": "NOT_FOUND", "message": str(e)}})


# Data operations


@app.post("/data/{namespace_name}/{table_name}", status_code=201)
def create_record(namespace_name: str, table_name: str, record_data: dict[str, Any]):
    try:
        # 获取命名空间和表
        namespace = namespaces_manager.get_namespace(namespace_name)
        table = namespace.get_table(table_name)

        record_id = record_data.get("id")
        data = record_data.get("data")

        if not record_id:
            raise ValueError("Record ID is required")
        if not data:
            raise ValueError("Record data is required")

        # 创建记录
        table.create_record(record_id, data)

        # 返回记录信息
        return {
            "id": record_id,
            "data": data
        }
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail={
                "error": {"code": "NOT_FOUND", "message": str(e)}})
        if "already exists" in str(e):
            raise HTTPException(status_code=409, detail={
                "error": {"code": "CONFLICT", "message": str(e)}})
        raise HTTPException(status_code=400, detail={
            "error": {"code": "BAD_REQUEST", "message": str(e)}})


@app.get("/data/{namespace_name}/{table_name}")
def list_records(namespace_name: str, table_name: str, page: int = 1, per_page: int = 20):
    try:
        # 获取命名空间和表
        namespace = namespaces_manager.get_namespace(namespace_name)
        table = namespace.get_table(table_name)

        # 获取记录列表
        record_ids = table.list_records()

        # 获取完整记录数据
        records = []
        for record_id in record_ids:
            record_data = table.get_record(record_id)
            records.append({
                "id": record_id,
                "data": record_data
            })

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


@app.get("/data/{namespace_name}/{table_name}/{record_id}")
def get_record(namespace_name: str, table_name: str, record_id: str):
    try:
        # 获取命名空间和表
        namespace = namespaces_manager.get_namespace(namespace_name)
        table = namespace.get_table(table_name)

        # 获取记录
        record_data = table.get_record(record_id)

        # 返回记录信息
        return {
            "id": record_id,
            "data": record_data
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail={
            "error": {"code": "NOT_FOUND", "message": str(e)}})


@app.put("/data/{namespace_name}/{table_name}/{record_id}")
def update_record(namespace_name: str, table_name: str, record_id: str, update_data: dict[str, Any]):
    try:
        # 获取命名空间和表
        namespace = namespaces_manager.get_namespace(namespace_name)
        table = namespace.get_table(table_name)

        data = update_data.get("data")
        if data is None:
            raise ValueError("Record data is required")

        # 更新记录
        table.update_record(record_id, data)

        # 返回更新后的记录信息
        return {
            "id": record_id,
            "data": data
        }
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail={
                "error": {"code": "NOT_FOUND", "message": str(e)}})
        raise HTTPException(status_code=400, detail={
            "error": {"code": "BAD_REQUEST", "message": str(e)}})


@app.delete("/data/{namespace_name}/{table_name}/{record_id}", status_code=204)
def delete_record(namespace_name: str, table_name: str, record_id: str):
    try:
        # 获取命名空间和表
        namespace = namespaces_manager.get_namespace(namespace_name)
        table = namespace.get_table(table_name)

        # 删除记录
        table.delete_record(record_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail={
            "error": {"code": "NOT_FOUND", "message": str(e)}})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

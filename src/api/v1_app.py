from typing import Any

from fastapi import HTTPException, Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from .v1 import (
    IDatabase, ITable, NamespaceCreateRequest, NamespaceUpdateRequest, NamespaceData,
    TableCreateRequest, TableUpdateRequest, TableData, ErrorResponse, INamespace,
)

app = FastAPI(
    prefix="/api/v1",
    tags=["v1"],
)


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    """Convert HTTPException to ErrorResponse format"""
    if isinstance(exc.detail, ErrorResponse):
        error_response = exc.detail
    else:
        error_response = ErrorResponse(
            message="Unknown Error",
            type="",
            data=None)
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )


def get_database() -> IDatabase:
    """Placeholder for database dependency injection"""
    raise NotImplementedError("Database provider not configured")


# Namespace endpoints


@app.post("/namespace", response_model=NamespaceData, status_code=201, tags=["Namespace"])
def create_namespace(
        namespace_data: NamespaceCreateRequest,
        db: IDatabase = Depends(get_database)
):
    namespaces = db.namespaces
    namespaces.create_namespace(namespace_data)

    return NamespaceData(
        name=namespace_data.name,
        description=namespace_data.description
    )


@app.get("/namespace", response_model=list[NamespaceData], tags=["Namespace"])
def list_namespaces(
        db: IDatabase = Depends(get_database)
):
    namespaces = db.namespaces
    return namespaces.list_namespaces()


@app.get("/namespace/{namespace}", response_model=NamespaceData, tags=["Namespace"])
def get_namespace(
        namespace: str,
        db: IDatabase = Depends(get_database)
):
    namespaces = db.namespaces
    namespaces_data = namespaces.get_namespace(namespace)
    if namespaces_data is None:
        raise HTTPException(
            status_code=404, detail=ErrorResponse(
                message=f"Namespace '{namespace}' not found",
                type="string",
                data=namespace))
    return namespaces_data


@app.put("/namespace/{namespace}", tags=["Namespace"])
def update_namespace(
        namespace: str,
        update_data: NamespaceUpdateRequest,
        db: IDatabase = Depends(get_database)
):
    namespaces = db.namespaces
    namespaces.update_namespace(namespace, update_data)

    return None


@app.delete("/namespace/{namespace}", status_code=204, tags=["Namespace"])
def delete_namespace(
        namespace: str,
        db: IDatabase = Depends(get_database)
):
    namespaces = db.namespaces
    namespaces.delete_namespace(namespace)
    return None


# Table endpoints


def load_namespace(db: IDatabase, namespace: str):
    namespace_obj = db.load_namespace(namespace)
    if namespace_obj is None:
        raise HTTPException(
            status_code=404, detail=ErrorResponse(
                message=f"Namespace '{namespace}' not found",
                type="string",
                data=namespace))
    return namespace_obj


@app.post("/table/{namespace}", response_model=TableData, status_code=201, tags=["Table"])
def create_table(
        namespace: str,
        table_data: TableCreateRequest,
        db: IDatabase = Depends(get_database)
):
    load_namespace(db, namespace).create_table(table_data)

    return TableData(
        name=table_data.name,
        description=table_data.description,
        namespace=namespace
    )


@app.get("/table/{namespace}", response_model=list[TableData], tags=["Table"])
def list_tables(
        namespace: str,
        db: IDatabase = Depends(get_database)
):
    namespace_obj = load_namespace(db, namespace)
    return namespace_obj.list_tables()


def get_table_meta(db: IDatabase, namespace: str, table: str) -> tuple[INamespace, TableData]:
    namespace_obj = db.load_namespace(namespace)
    if namespace_obj is None:
        # Due to the error handler, here won't call load_namespace again
        raise HTTPException(
            status_code=404, detail=ErrorResponse(
                message=f"Namespace '{namespace}' not found",
                type="object",
                data={"namespace": namespace}))
    table_obj = namespace_obj.get_table(table)
    if table_obj is None:
        raise HTTPException(
            status_code=404, detail=ErrorResponse(
                message=f"Table '{table}' not found in namespace '{namespace}'",
                type="object",
                data={"namespace": namespace, "table": table}))
    return namespace_obj, table_obj


@app.get("/table/{namespace}/{table}", response_model=TableData, tags=["Table"])
def get_table(
        namespace: str,
        table: str,
        db: IDatabase = Depends(get_database)
):
    _, table_obj = get_table_meta(db, namespace, table)
    return table_obj


@app.put("/table/{namespace}/{table}", tags=["Table"])
def update_table(
        namespace: str,
        table: str,
        update_data: TableUpdateRequest,
        db: IDatabase = Depends(get_database)
):
    namespace_obj, _ = get_table_meta(db, namespace, table)
    namespace_obj.update_table(table, update_data)

    return None


@app.delete("/table/{namespace}/{table}", status_code=204, tags=["Table"])
def delete_table(
        namespace: str,
        table: str,
        db: IDatabase = Depends(get_database)
):
    namespace_obj, _ = get_table_meta(db, namespace, table)
    namespace_obj.delete_table(table)
    return None


# Record endpoints

def load_table(db: IDatabase, namespace: str, table: str) -> ITable:
    namespace_obj = db.load_namespace(namespace)
    if namespace_obj is None:
        raise HTTPException(
            status_code=404, detail=ErrorResponse(
                message=f"Namespace '{namespace}' not found",
                type="object",
                data={"namespace": namespace}))
    table_obj = namespace_obj.load_table(table)
    if table_obj is None:
        raise HTTPException(
            status_code=404, detail=ErrorResponse(
                message=f"Table '{table}' not found in namespace '{namespace}'",
                type="object",
                data={"namespace": namespace, "table": table}))
    return table_obj


@app.post("/data/{namespace}/{table}/{record_id}", status_code=201, tags=["Record"])
def create_record(
        namespace: str,
        table: str,
        record_id: str,
        data: Any,
        db: IDatabase = Depends(get_database)
):
    load_table(db, namespace, table).create_record(
        record_id=record_id, data=data)
    return None


@app.get("/data/{namespace}/{table}", response_model=list[str], tags=["Record"])
def list_records(
        namespace: str,
        table: str,
        db: IDatabase = Depends(get_database)
):
    table_obj = load_table(db, namespace, table)
    return table_obj.list_records()


def load_table_get_record(db: IDatabase, namespace: str,
                          table: str,
                          record_id: str) -> tuple[ITable, Any]:
    table_obj = load_table(db, namespace, table)
    record_data = table_obj.get_record(record_id)
    if record_data is None:
        raise HTTPException(
            status_code=404, detail=ErrorResponse(
                message=f"Record '{record_id}' not found in table '{table}' in namespace '{namespace}'",
                type="object",
                data={"namespace": namespace, "table": table, "record_id": record_id}))
    return table_obj, record_data


@app.get("/data/{namespace}/{table}/{record_id}", response_model=dict, tags=["Record"])
def get_record(
        namespace: str,
        table: str,
        record_id: str,
        db: IDatabase = Depends(get_database)
):
    _, record_data = load_table_get_record(db, namespace, table, record_id)
    return record_data


@app.put("/data/{namespace}/{table}/{record_id}", tags=["Record"])
def update_record(
        namespace: str,
        table: str,
        record_id: str,
        data: Any,
        db: IDatabase = Depends(get_database)
):
    table_obj, _ = load_table_get_record(db, namespace, table, record_id)
    table_obj.update_record(
        record_id=record_id,
        data=data
    )

    return None


@app.delete("/data/{namespace}/{table}/{record_id}", status_code=204, tags=["Record"])
def delete_record(
        namespace: str,
        table: str,
        record_id: str,
        db: IDatabase = Depends(get_database)
):
    table_obj, _ = load_table_get_record(db, namespace, table, record_id)
    table_obj.delete_record(record_id)
    return None

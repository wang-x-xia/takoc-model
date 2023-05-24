import {TypeSystem} from "../typesystem/typesystem";

export default function (typeSystem: TypeSystem) {
    typeSystem.newType(
        {
            "name": "string",
            "description": "A well-known type that include all types of string that may have control character or error character"
        }
    )

    typeSystem.newType(
        {
            "name": "text",
            "description": "A string that can be readable, include some weird blank or format, but doesn't include the Cc char like NULL"
        }
    )

    typeSystem.canAssignTo({
        "assign": "text",
        "to": "string"
    })

    typeSystem.newType(
        {
            "name": "single-line",
            "description": "A text which only has one line"
        }
    )

    typeSystem.canAssignTo({
        "assign": "single-line",
        "to": "text"
    })

    typeSystem.newType(
        {
            "name": "lines",
            "description": "A text that may have one line or multiple lines"
        }
    )

    typeSystem.canAssignTo({
        "assign": "lines",
        "to": "text"
    })

    typeSystem.canAssignTo({
        "assign": "single-lines",
        "to": "lines"
    })
}

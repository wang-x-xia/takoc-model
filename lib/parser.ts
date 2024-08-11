import {Project, SourceFile, TypeNode} from "ts-morph";
import type {
    TypescriptElement,
    TypescriptFile,
    TypescriptFilePath,
    TypescriptLiteralType,
    TypescriptLiteralValue
} from "./core";

/**
 * Parses a TypeScript file and returns a list of elements.
 *
 * @param filePath
 * @returns elements
 */
export function parseTsFile(filePath: TypescriptFilePath): TypescriptFile {
    const sourceFile = readTypescriptFile(filePath)

    const elements: TypescriptElement[] = [];

    // Extract variables
    sourceFile.getVariableDeclarations().forEach((variable) => {
        elements.push({
            name: variable.getName(),
            type: "variable",
        });
    });

    // Extract types
    sourceFile.getTypeAliases().forEach((typeAlias) => {
        elements.push({
            name: typeAlias.getName(),
            type: "type",
        });
    });

    // Extract function as variable
    sourceFile.getFunctions().forEach((functionDeclaration) => {
        elements.push({
            name: functionDeclaration.getName(),
            type: "variable",
        });
    });

    // Extract class as variable
    sourceFile.getClasses().forEach((classDeclaration) => {
        elements.push({
            name: classDeclaration.getName(),
            type: "variable",
        });
    });

    // Extract interface as type
    sourceFile.getInterfaces().forEach((interfaceDeclaration) => {
        elements.push({
            name: interfaceDeclaration.getName(),
            type: "type",
        });
    })

    // Extract enum as type
    sourceFile.getEnums().forEach((enumDeclaration) => {
        elements.push({
            name: enumDeclaration.getName(),
            type: "type",
        });
    });

    return {
        elements,
    }
}

export function resolveTypescriptLiteralType(filePath: TypescriptFilePath, type: TypescriptElement): TypescriptLiteralType {
    const sourceFile = readTypescriptFile(filePath)

    const typeAlias = sourceFile.getTypeAlias(type["name"])

    const values: TypescriptLiteralValue[] = []

    function collectLiteral(node: TypeNode) {
        if (TypeNode.isLiteralTypeNode(node)) {
            const value = node.getLiteral()
            if (TypeNode.isStringLiteral(value)) {
                values.push(value.getLiteralValue())
            } else if (TypeNode.isNumericLiteral(value)) {
                values.push(value.getLiteralValue())
            } else {
                throw new Error("Unknown Literal Type")
            }
        } else if (TypeNode.isUnionTypeNode(node)) {
            node.getTypeNodes().forEach(child => collectLiteral(child))
        } else {
            throw new Error("Unknown Literal Type")
        }
    }

    collectLiteral(typeAlias.getTypeNodeOrThrow("Unknown Node for Type Alias"))
    return {
        "values": values,
    }
}


export function readTypescriptFile(filePath: TypescriptFilePath): SourceFile {
    const project = new Project();
    return project.addSourceFileAtPath(filePath);
}
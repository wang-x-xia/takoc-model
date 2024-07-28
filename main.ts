import type {TypescriptElement} from "./lib/core";
import {generateConstructorMethodForTypescriptLiteralType, replaceGeneratedMethod} from "./lib/generator";
import {parseTsFile, resolveTypescriptLiteralType} from "./lib/parser";

console.log(parseTsFile("lib/core.ts"))
console.log(parseTsFile("lib/parser.ts"))
const typescriptElementTypeElement: TypescriptElement = {"name": "TypescriptElementType", "type": "type"}
console.log({typescriptElementTypeElement})
const typescriptElementTypeLiteralType = resolveTypescriptLiteralType("lib/core.ts", typescriptElementTypeElement)
console.log({typescriptElementTypeLiteralType})
const typescriptElementTypeConstructor = generateConstructorMethodForTypescriptLiteralType(typescriptElementTypeElement, typescriptElementTypeLiteralType)
console.log({typescriptElementTypeConstructor})
replaceGeneratedMethod("lib/core.ts", typescriptElementTypeConstructor)
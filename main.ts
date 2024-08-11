import {
    generateConstructorMethodForTypescriptInterface,
    generateConstructorMethodForTypescriptLiteralType,
    generateConstructorMethodForTypescriptString,
    replaceGeneratedMethod
} from "./lib/generator";
import {parseTsFile, resolveTypescriptLiteralType} from "./lib/parser";

const coreTsTypescriptElements = parseTsFile("lib/core.ts");
console.log({coreTsTypescriptElements})
const parseTsTypescriptElements = parseTsFile("lib/parser.ts");
console.log({parseTsTypescriptElements})
const typescriptElementTypeElement = coreTsTypescriptElements.filter(it => it.name === "TypescriptElementType")[0]
console.log({typescriptElementTypeElement})
const typescriptElementTypeLiteralType = resolveTypescriptLiteralType("lib/core.ts", typescriptElementTypeElement)
console.log({typescriptElementTypeLiteralType})
const typescriptElementTypeConstructor = generateConstructorMethodForTypescriptLiteralType(typescriptElementTypeElement, typescriptElementTypeLiteralType)
console.log({typescriptElementTypeConstructor})
replaceGeneratedMethod("lib/core.ts", typescriptElementTypeConstructor)

const typescriptIdentifierTypeElement = coreTsTypescriptElements.filter(it => it.name === "TypescriptIdentifier")[0]
const checkTypescriptIdentifierTypeElement = coreTsTypescriptElements.filter(it => it.name === "checkTypescriptIdentifier")[0]
const typescriptIdentifierConstructor = generateConstructorMethodForTypescriptString(typescriptIdentifierTypeElement, checkTypescriptIdentifierTypeElement)
replaceGeneratedMethod("lib/core.ts", typescriptIdentifierConstructor)


const typescriptTypeElement = coreTsTypescriptElements.filter(it => it.name === "TypescriptElement")[0]
const constructorMethodForTypescriptInterface = generateConstructorMethodForTypescriptInterface(typescriptTypeElement, {
    fields: [{
        name: "name",
        method: coreTsTypescriptElements.filter(it => it.name === "createTypescriptIdentifier")[0],
    }, {
        name: "type",
        method: coreTsTypescriptElements.filter(it => it.name === "createTypescriptElementType")[0],
    }
    ]
});
replaceGeneratedMethod("lib/core.ts", constructorMethodForTypescriptInterface)

import {extractCheckerFunction} from "./lib/checker";
import {
    generateConstructorMethodForTypescriptInterface,
    generateConstructorMethodForTypescriptLiteralType,
    generateConstructorMethodForTypescriptString
} from "./lib/constructor";
import {findElement} from "./lib/file";
import {replaceGeneratedMethod} from "./lib/generator";
import {parseTsFile, resolveTypescriptLiteralType} from "./lib/parser";

const coreTsTypescriptElements = parseTsFile("lib/core.ts");
console.log({coreTsTypescriptElements})
const parseTsTypescriptElements = parseTsFile("lib/parser.ts");
console.log({parseTsTypescriptElements})
const typescriptElementTypeElement = findElement(coreTsTypescriptElements, "TypescriptElementType", "type")
console.log({typescriptElementTypeElement})
const typescriptElementTypeLiteralType = resolveTypescriptLiteralType("lib/core.ts", typescriptElementTypeElement)
console.log({typescriptElementTypeLiteralType})
const typescriptElementTypeConstructor = generateConstructorMethodForTypescriptLiteralType(typescriptElementTypeElement, typescriptElementTypeLiteralType)
console.log({typescriptElementTypeConstructor})
replaceGeneratedMethod("lib/core.ts", typescriptElementTypeConstructor)

const typescriptIdentifierTypeElement = findElement(coreTsTypescriptElements, "TypescriptIdentifier", "type")
const checkTypescriptIdentifierTypeElement = findElement(coreTsTypescriptElements, "checkTypescriptIdentifier", "variable")
const typescriptIdentifierConstructor = generateConstructorMethodForTypescriptString(typescriptIdentifierTypeElement, checkTypescriptIdentifierTypeElement)
replaceGeneratedMethod("lib/core.ts", typescriptIdentifierConstructor)


const typescriptTypeElement = coreTsTypescriptElements.elements.filter(it => it.name === "TypescriptElement")[0]
const constructorMethodForTypescriptInterface = generateConstructorMethodForTypescriptInterface(typescriptTypeElement, {
    fields: [{
        name: "name",
        method: coreTsTypescriptElements.elements.filter(it => it.name === "createTypescriptIdentifier")[0],
    }, {
        name: "type",
        method: coreTsTypescriptElements.elements.filter(it => it.name === "createTypescriptElementType")[0],
    }
    ]
});
replaceGeneratedMethod("lib/core.ts", constructorMethodForTypescriptInterface)


const checker = extractCheckerFunction("lib/core.ts", checkTypescriptIdentifierTypeElement, coreTsTypescriptElements)
console.log({checker})
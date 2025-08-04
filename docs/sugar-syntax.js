(function () {
    function init() {
        Prism.languages.sugar = {
            comment: { pattern: /\/\/.*/, greedy: true },
            string: { pattern: /"(?:\\.|[^"\\])*"/, greedy: true },
            char: { pattern: /'(?:\\.|[^'\\])'/, greedy: true },
            number: { pattern: /\b\d+(?:\.\d+)?\b/ },
            boolean: { pattern: /:T:|:F:/, greedy: true },
            keyword: { pattern: /\b(?:DEF|CLASS|PUBLIC|PRIVATE|PROTECTED|STATIC|OVERRIDE|CONSTRUCTOR|INTERFACE|TYPE|EXTENDS|IMPLEMENTS|FUNC|END|THIS|SUPER|IMPORT|IF|DO|ELSE|ELIF|FOR|IN|WHILE|TRY|CATCH|FINALLY|MATCH|CASE|DEFAULT|RETURN|THROW|SPAWN)\b/ },
            operator: { pattern: /(?::=|==|!=|<=|>=|<|>|\+|-|\*|\/|%|&&|\|\||!|->|\.|,|=|:|\$)/ },
            'method-call': { pattern: /:[A-Z][A-Z0-9_]*:/, alias: 'function' },
            type: { pattern: /#(?:int|float|bool|char|str|void|any|[a-zA-Z_][a-zA-Z0-9_]*)/ },
            identifier: { pattern: /\b[a-zA-Z_][a-zA-Z0-9_]*\b/ },
            punctuation: { pattern: /[{}\[\];(),.]/ }
        };
    }
    if (typeof Prism === 'undefined') {
        window.addEventListener('load', () => { if (typeof Prism !== 'undefined') init(); });
    } else {
        init();
    }
})();
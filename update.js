const fs = require("fs");

const data = {
    paivitetty: new Date().toISOString().split("T")[0],
    lahde: "polttoaine.net",

    eilisen_keskihinnat: {
        "95E10": "2.141",
        "98E5": "2.252",
        "Diesel": "2.328"
    }
};

fs.writeFileSync(
    "data.json",
    JSON.stringify(data, null, 2)
);

console.log("data.json päivitetty");

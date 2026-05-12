const fs = require("fs");
const cheerio = require("cheerio");

async function getPrices() {
    const res = await fetch("https://polttoaine.net");
    const html = await res.text();

    const $ = cheerio.load(html);

    // ⚠️ NÄMÄ SELECTORIT PITÄÄ TARKISTAA SIVUSTOSTA
    const diesel = $(".diesel-price").first().text().trim();
    const e95 = $(".e95-price").first().text().trim();
    const e98 = $(".e98-price").first().text().trim();

    return {
        "95E10": e95,
        "98E5": e98,
        "Diesel": diesel
    };
}

async function main() {
    const prices = await getPrices();

    const data = {
        paivitetty: new Date().toISOString(),
        lahde: "polttoaine.net",

        eilisen_keskihinnat: prices
    };

    fs.writeFileSync("data.json", JSON.stringify(data, null, 2));

    console.log("Päivitetty:", data);
}

main();

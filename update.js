const fs = require("fs");

async function getPrices() {
    const res = await fetch("https://polttoaine.net");
    const html = await res.text();

    const match = html.match(/<tr class="bg2">([\s\S]*?)<\/tr>/);

    if (!match) throw new Error("Riviä ei löytynyt");

    const row = match[1];

    const prices = [...row.matchAll(/<td class="Hinnat">(.*?)<\/td>/g)]
        .map(m => m[1]);

    return {
        "95E10": prices[0],
        "98E5": prices[1],
        "Diesel": prices[2]
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

main();const fs = require("fs");
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

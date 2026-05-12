const fs = require("fs");

async function getPrices() {
    const res = await fetch("https://polttoaine.net");
    // Sivusto käyttää latin1-enkoodausta, täytyy muuntaa
    const buffer = await res.arrayBuffer();
    const html = new TextDecoder("latin1").decode(buffer);

    // Haetaan "Eilisen keskihinnat" -rivi taulukosta
    // Rakenne: <tr class="bg2"><td ...></td><td class="Hinnat">2.141</td>...
    const match = html.match(/Eilisen keskihinnat[\s\S]*?<tr[^>]*>([\s\S]*?)<\/tr>/);
    if (!match) throw new Error("Eilisen keskihinnat -riviä ei löytynyt");

    const row = match[1];
    const prices = [...row.matchAll(/<td[^>]*class="Hinnat"[^>]*>(.*?)<\/td>/g)]
        .map(m => m[1].trim());

    if (prices.length < 3) throw new Error(`Liian vähän hintoja löytyi: ${prices.length}`);

    return {
        "95E10": prices[0],
        "98E5": prices[1],
        "Diesel": prices[2]
    };
}

async function main() {
    try {
        const prices = await getPrices();
        const data = {
            paivitetty: new Date().toISOString(),
            lahde: "polttoaine.net",
            eilisen_keskihinnat: prices
        };
        fs.writeFileSync("data.json", JSON.stringify(data, null, 2));
        console.log("Päivitetty:", data);
    } catch (err) {
        console.error("Virhe:", err.message);
        process.exit(1);
    }
}

main();

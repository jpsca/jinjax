var lunr = require("lunr");
require("lunr-languages/lunr.stemmer.support")(lunr);
const fs = require("node:fs");

function build_index([lang, outpath]) {
  lang = lang || "en"
  outpath = outpath || "."

  if (lang !== "en") {
    const lunr_lang = require(`lunr-languages/lunr.${lang}`)(lunr);
    this.use(lunr_lang);
  }

  const idx = lunr(function() {
    this.ref("id");
    this.field("title", { boost: 10 });
    this.field("body");
    const docs =  JSON.parse(fs.readFileSync(`${outpath}/docs-${lang}.json`));

    for (let doc in docs) {
      this.add(doc)
    }
  })
  fs.writeFileSync(`${outpath}/search-${lang}.json`, JSON.stringify(idx));
}

build_index(process.argv.slice(2));

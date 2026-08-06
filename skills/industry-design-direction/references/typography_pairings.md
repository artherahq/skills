# Font pairings

All Google Fonts, so all free and self-hostable. Copy the `@import` line into
your stylesheet and the Tailwind snippet into `tailwind.config.js`.

Pairing beats picking: the heading/body split is what stops a page reading as
one undifferentiated block. A single family everywhere (the Inter-for-everything
default) is the most common reason a generated page looks templated.

## Classic Elegant — Serif + Sans

- **Heading**: Playfair Display
- **Body**: Inter
- **Mood**: elegant, luxury, sophisticated, timeless, premium, editorial
- **Best for**: Luxury brands, fashion, spa, beauty, editorial, magazines, high-end e-commerce
- **Note**: High contrast between elegant heading and clean body. Perfect for luxury/premium.

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;500;600;700&display=swap');
```

```js
fontFamily: { serif: ['Playfair Display', 'serif'], sans: ['Inter', 'sans-serif'] }
```

## Modern Professional — Sans + Sans

- **Heading**: Poppins
- **Body**: Open Sans
- **Mood**: modern, professional, clean, corporate, friendly, approachable
- **Best for**: SaaS, corporate sites, business apps, startups, professional services
- **Note**: Geometric Poppins for headings, humanist Open Sans for readability.

```css
@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap');
```

```js
fontFamily: { heading: ['Poppins', 'sans-serif'], body: ['Open Sans', 'sans-serif'] }
```

## Tech Startup — Sans + Sans

- **Heading**: Space Grotesk
- **Body**: DM Sans
- **Mood**: tech, startup, modern, innovative, bold, futuristic
- **Best for**: Tech companies, startups, SaaS, developer tools, AI products
- **Note**: Space Grotesk has unique character, DM Sans is highly readable.

```css
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
```

```js
fontFamily: { heading: ['Space Grotesk', 'sans-serif'], body: ['DM Sans', 'sans-serif'] }
```

## Editorial Classic — Serif + Serif

- **Heading**: Cormorant Garamond
- **Body**: Libre Baskerville
- **Mood**: editorial, classic, literary, traditional, refined, bookish
- **Best for**: Publishing, blogs, news sites, literary magazines, book covers
- **Note**: All-serif pairing for traditional editorial feel.

```css
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Libre+Baskerville:wght@400;700&display=swap');
```

```js
fontFamily: { heading: ['Cormorant Garamond', 'serif'], body: ['Libre Baskerville', 'serif'] }
```

## Minimal Swiss — Sans + Sans

- **Heading**: Inter
- **Body**: Inter
- **Mood**: minimal, clean, swiss, functional, neutral, professional
- **Best for**: Dashboards, admin panels, documentation, enterprise apps, design systems
- **Note**: Single font family with weight variations. Ultimate simplicity.

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
```

```js
fontFamily: { sans: ['Inter', 'sans-serif'] }
```

## Playful Creative — Display + Sans

- **Heading**: Fredoka
- **Body**: Nunito
- **Mood**: playful, friendly, fun, creative, warm, approachable
- **Best for**: Children's apps, educational, gaming, creative tools, entertainment
- **Note**: Rounded, friendly fonts perfect for playful UIs.

```css
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&family=Nunito:wght@300;400;500;600;700&display=swap');
```

```js
fontFamily: { heading: ['Fredoka', 'sans-serif'], body: ['Nunito', 'sans-serif'] }
```

## Bold Statement — Display + Sans

- **Heading**: Bebas Neue
- **Body**: Source Sans 3
- **Mood**: bold, impactful, strong, dramatic, modern, headlines
- **Best for**: Marketing sites, portfolios, agencies, event pages, sports
- **Note**: Bebas Neue for large headlines only. All-caps display font.

```css
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Source+Sans+3:wght@300;400;500;600;700&display=swap');
```

```js
fontFamily: { display: ['Bebas Neue', 'sans-serif'], body: ['Source Sans 3', 'sans-serif'] }
```

## Wellness Calm — Serif + Sans

- **Heading**: Lora
- **Body**: Raleway
- **Mood**: calm, wellness, health, relaxing, natural, organic
- **Best for**: Health apps, wellness, spa, meditation, yoga, organic brands
- **Note**: Lora's organic curves with Raleway's elegant simplicity.

```css
@import url('https://fonts.googleapis.com/css2?family=Lora:wght@400;500;600;700&family=Raleway:wght@300;400;500;600;700&display=swap');
```

```js
fontFamily: { serif: ['Lora', 'serif'], sans: ['Raleway', 'sans-serif'] }
```

## Developer Mono — Mono + Sans

- **Heading**: JetBrains Mono
- **Body**: IBM Plex Sans
- **Mood**: code, developer, technical, precise, functional, hacker
- **Best for**: Developer tools, documentation, code editors, tech blogs, CLI apps
- **Note**: JetBrains for code, IBM Plex for UI. Developer-focused.

```css
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');
```

```js
fontFamily: { mono: ['JetBrains Mono', 'monospace'], sans: ['IBM Plex Sans', 'sans-serif'] }
```

## Retro Vintage — Display + Serif

- **Heading**: Abril Fatface
- **Body**: Merriweather
- **Mood**: retro, vintage, nostalgic, dramatic, decorative, bold
- **Best for**: Vintage brands, breweries, restaurants, creative portfolios, posters
- **Note**: Abril Fatface for hero headlines only. High-impact vintage feel.

```css
@import url('https://fonts.googleapis.com/css2?family=Abril+Fatface&family=Merriweather:wght@300;400;700&display=swap');
```

```js
fontFamily: { display: ['Abril Fatface', 'serif'], body: ['Merriweather', 'serif'] }
```

## Geometric Modern — Sans + Sans

- **Heading**: Outfit
- **Body**: Work Sans
- **Mood**: geometric, modern, clean, balanced, contemporary, versatile
- **Best for**: General purpose, portfolios, agencies, modern brands, landing pages
- **Note**: Both geometric but Outfit more distinctive for headings.

```css
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Work+Sans:wght@300;400;500;600;700&display=swap');
```

```js
fontFamily: { heading: ['Outfit', 'sans-serif'], body: ['Work Sans', 'sans-serif'] }
```

## Luxury Serif — Serif + Sans

- **Heading**: Cormorant
- **Body**: Montserrat
- **Mood**: luxury, high-end, fashion, elegant, refined, premium
- **Best for**: Fashion brands, luxury e-commerce, jewelry, high-end services
- **Note**: Cormorant's elegance with Montserrat's geometric precision.

```css
@import url('https://fonts.googleapis.com/css2?family=Cormorant:wght@400;500;600;700&family=Montserrat:wght@300;400;500;600;700&display=swap');
```

```js
fontFamily: { serif: ['Cormorant', 'serif'], sans: ['Montserrat', 'sans-serif'] }
```

## Friendly SaaS — Sans + Sans

- **Heading**: Plus Jakarta Sans
- **Body**: Plus Jakarta Sans
- **Mood**: friendly, modern, saas, clean, approachable, professional
- **Best for**: SaaS products, web apps, dashboards, B2B, productivity tools
- **Note**: Single versatile font. Modern alternative to Inter.

```css
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
```

```js
fontFamily: { sans: ['Plus Jakarta Sans', 'sans-serif'] }
```

## News Editorial — Serif + Sans

- **Heading**: Newsreader
- **Body**: Roboto
- **Mood**: news, editorial, journalism, trustworthy, readable, informative
- **Best for**: News sites, blogs, magazines, journalism, content-heavy sites
- **Note**: Newsreader designed for long-form reading. Roboto for UI.

```css
@import url('https://fonts.googleapis.com/css2?family=Newsreader:wght@400;500;600;700&family=Roboto:wght@300;400;500;700&display=swap');
```

```js
fontFamily: { serif: ['Newsreader', 'serif'], sans: ['Roboto', 'sans-serif'] }
```

## Handwritten Charm — Script + Sans

- **Heading**: Caveat
- **Body**: Quicksand
- **Mood**: handwritten, personal, friendly, casual, warm, charming
- **Best for**: Personal blogs, invitations, creative portfolios, lifestyle brands
- **Note**: Use Caveat sparingly for accents. Quicksand for body.

```css
@import url('https://fonts.googleapis.com/css2?family=Caveat:wght@400;500;600;700&family=Quicksand:wght@300;400;500;600;700&display=swap');
```

```js
fontFamily: { script: ['Caveat', 'cursive'], sans: ['Quicksand', 'sans-serif'] }
```

## Corporate Trust — Sans + Sans

- **Heading**: Lexend
- **Body**: Source Sans 3
- **Mood**: corporate, trustworthy, accessible, readable, professional, clean
- **Best for**: Enterprise, government, healthcare, finance, accessibility-focused
- **Note**: Lexend designed for readability. Excellent accessibility.

```css
@import url('https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;500;600;700&family=Source+Sans+3:wght@300;400;500;600;700&display=swap');
```

```js
fontFamily: { heading: ['Lexend', 'sans-serif'], body: ['Source Sans 3', 'sans-serif'] }
```

## Brutalist Raw — Mono + Mono

- **Heading**: Space Mono
- **Body**: Space Mono
- **Mood**: brutalist, raw, technical, monospace, minimal, stark
- **Best for**: Brutalist designs, developer portfolios, experimental, tech art
- **Note**: All-mono for raw brutalist aesthetic. Limited weights.

```css
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap');
```

```js
fontFamily: { mono: ['Space Mono', 'monospace'] }
```

## Fashion Forward — Sans + Sans

- **Heading**: Syne
- **Body**: Manrope
- **Mood**: fashion, avant-garde, creative, bold, artistic, edgy
- **Best for**: Fashion brands, creative agencies, art galleries, design studios
- **Note**: Syne's unique character for headlines. Manrope for readability.

```css
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700&family=Syne:wght@400;500;600;700&display=swap');
```

```js
fontFamily: { heading: ['Syne', 'sans-serif'], body: ['Manrope', 'sans-serif'] }
```

## Soft Rounded — Sans + Sans

- **Heading**: Varela Round
- **Body**: Nunito Sans
- **Mood**: soft, rounded, friendly, approachable, warm, gentle
- **Best for**: Children's products, pet apps, friendly brands, wellness, soft UI
- **Note**: Both rounded and friendly. Perfect for soft UI designs.

```css
@import url('https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@300;400;500;600;700&family=Varela+Round&display=swap');
```

```js
fontFamily: { heading: ['Varela Round', 'sans-serif'], body: ['Nunito Sans', 'sans-serif'] }
```

## Premium Sans — Sans + Sans

- **Heading**: Satoshi
- **Body**: General Sans
- **Mood**: premium, modern, clean, sophisticated, versatile, balanced
- **Best for**: Premium brands, modern agencies, SaaS, portfolios, startups
- **Note**: Note: Satoshi/General Sans on Fontshare. DM Sans as Google alternative.

```css
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
```

```js
fontFamily: { sans: ['DM Sans', 'sans-serif'] }
```

## Vietnamese Friendly — Sans + Sans

- **Heading**: Be Vietnam Pro
- **Body**: Noto Sans
- **Mood**: vietnamese, international, readable, clean, multilingual, accessible
- **Best for**: Vietnamese sites, multilingual apps, international products
- **Note**: Be Vietnam Pro excellent Vietnamese support. Noto as fallback.

```css
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;500;600;700&family=Noto+Sans:wght@300;400;500;600;700&display=swap');
```

```js
fontFamily: { sans: ['Be Vietnam Pro', 'Noto Sans', 'sans-serif'] }
```

## Japanese Elegant — Serif + Sans

- **Heading**: Noto Serif JP
- **Body**: Noto Sans JP
- **Mood**: japanese, elegant, traditional, modern, multilingual, readable
- **Best for**: Japanese sites, Japanese restaurants, cultural sites, anime/manga
- **Note**: Noto fonts excellent Japanese support. Traditional + modern feel.

```css
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&family=Noto+Serif+JP:wght@400;500;600;700&display=swap');
```

```js
fontFamily: { serif: ['Noto Serif JP', 'serif'], sans: ['Noto Sans JP', 'sans-serif'] }
```

## Korean Modern — Sans + Sans

- **Heading**: Noto Sans KR
- **Body**: Noto Sans KR
- **Mood**: korean, modern, clean, professional, multilingual, readable
- **Best for**: Korean sites, K-beauty, K-pop, Korean businesses, multilingual
- **Note**: Clean Korean typography. Single font with weight variations.

```css
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
```

```js
fontFamily: { sans: ['Noto Sans KR', 'sans-serif'] }
```

## Chinese Traditional — Serif + Sans

- **Heading**: Noto Serif TC
- **Body**: Noto Sans TC
- **Mood**: chinese, traditional, elegant, cultural, multilingual, readable
- **Best for**: Traditional Chinese sites, cultural content, Taiwan/Hong Kong markets
- **Note**: Traditional Chinese character support. Elegant pairing.

```css
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&family=Noto+Serif+TC:wght@400;500;600;700&display=swap');
```

```js
fontFamily: { serif: ['Noto Serif TC', 'serif'], sans: ['Noto Sans TC', 'sans-serif'] }
```

## Chinese Simplified — Sans + Sans

- **Heading**: Noto Sans SC
- **Body**: Noto Sans SC
- **Mood**: chinese, simplified, modern, professional, multilingual, readable
- **Best for**: Simplified Chinese sites, mainland China market, business apps
- **Note**: Simplified Chinese support. Clean modern look.

```css
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');
```

```js
fontFamily: { sans: ['Noto Sans SC', 'sans-serif'] }
```

## Arabic Elegant — Serif + Sans

- **Heading**: Noto Naskh Arabic
- **Body**: Noto Sans Arabic
- **Mood**: arabic, elegant, traditional, cultural, RTL, readable
- **Best for**: Arabic sites, Middle East market, Islamic content, bilingual sites
- **Note**: RTL support. Naskh for traditional, Sans for modern Arabic.

```css
@import url('https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@400;500;600;700&family=Noto+Sans+Arabic:wght@300;400;500;700&display=swap');
```

```js
fontFamily: { serif: ['Noto Naskh Arabic', 'serif'], sans: ['Noto Sans Arabic', 'sans-serif'] }
```

## Thai Modern — Sans + Sans

- **Heading**: Noto Sans Thai
- **Body**: Noto Sans Thai
- **Mood**: thai, modern, readable, clean, multilingual, accessible
- **Best for**: Thai sites, Southeast Asia, tourism, Thai restaurants
- **Note**: Clean Thai typography. Excellent readability.

```css
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;500;700&display=swap');
```

```js
fontFamily: { sans: ['Noto Sans Thai', 'sans-serif'] }
```

## Hebrew Modern — Sans + Sans

- **Heading**: Noto Sans Hebrew
- **Body**: Noto Sans Hebrew
- **Mood**: hebrew, modern, RTL, clean, professional, readable
- **Best for**: Hebrew sites, Israeli market, Jewish content, bilingual sites
- **Note**: RTL support. Clean modern Hebrew typography.

```css
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Hebrew:wght@300;400;500;700&display=swap');
```

```js
fontFamily: { sans: ['Noto Sans Hebrew', 'sans-serif'] }
```

## Legal Professional — Serif + Sans

- **Heading**: EB Garamond
- **Body**: Lato
- **Mood**: legal, professional, traditional, trustworthy, formal, authoritative
- **Best for**: Law firms, legal services, contracts, formal documents, government
- **Note**: EB Garamond for authority. Lato for clean body text.

```css
@import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500;600;700&family=Lato:wght@300;400;700&display=swap');
```

```js
fontFamily: { serif: ['EB Garamond', 'serif'], sans: ['Lato', 'sans-serif'] }
```

## Medical Clean — Sans + Sans

- **Heading**: Figtree
- **Body**: Noto Sans
- **Mood**: medical, clean, accessible, professional, healthcare, trustworthy
- **Best for**: Healthcare, medical clinics, pharma, health apps, accessibility
- **Note**: Clean, accessible fonts for medical contexts.

```css
@import url('https://fonts.googleapis.com/css2?family=Figtree:wght@300;400;500;600;700&family=Noto+Sans:wght@300;400;500;700&display=swap');
```

```js
fontFamily: { heading: ['Figtree', 'sans-serif'], body: ['Noto Sans', 'sans-serif'] }
```

## Financial Trust — Sans + Sans

- **Heading**: IBM Plex Sans
- **Body**: IBM Plex Sans
- **Mood**: financial, trustworthy, professional, corporate, banking, serious
- **Best for**: Banks, finance, insurance, investment, fintech, enterprise
- **Note**: IBM Plex conveys trust and professionalism. Excellent for data.

```css
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');
```

```js
fontFamily: { sans: ['IBM Plex Sans', 'sans-serif'] }
```

## Real Estate Luxury — Serif + Sans

- **Heading**: Cinzel
- **Body**: Josefin Sans
- **Mood**: real estate, luxury, elegant, sophisticated, property, premium
- **Best for**: Real estate, luxury properties, architecture, interior design
- **Note**: Cinzel's elegance for headlines. Josefin for modern body.

```css
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700&family=Josefin+Sans:wght@300;400;500;600;700&display=swap');
```

```js
fontFamily: { serif: ['Cinzel', 'serif'], sans: ['Josefin Sans', 'sans-serif'] }
```

## Restaurant Menu — Serif + Sans

- **Heading**: Playfair Display SC
- **Body**: Karla
- **Mood**: restaurant, menu, culinary, elegant, foodie, hospitality
- **Best for**: Restaurants, cafes, food blogs, culinary, hospitality
- **Note**: Small caps Playfair for menu headers. Karla for descriptions.

```css
@import url('https://fonts.googleapis.com/css2?family=Karla:wght@300;400;500;600;700&family=Playfair+Display+SC:wght@400;700&display=swap');
```

```js
fontFamily: { display: ['Playfair Display SC', 'serif'], sans: ['Karla', 'sans-serif'] }
```

## Art Deco — Display + Sans

- **Heading**: Poiret One
- **Body**: Didact Gothic
- **Mood**: art deco, vintage, 1920s, elegant, decorative, gatsby
- **Best for**: Vintage events, art deco themes, luxury hotels, classic cocktails
- **Note**: Poiret One for art deco headlines only. Didact for body.

```css
@import url('https://fonts.googleapis.com/css2?family=Didact+Gothic&family=Poiret+One&display=swap');
```

```js
fontFamily: { display: ['Poiret One', 'sans-serif'], sans: ['Didact Gothic', 'sans-serif'] }
```

## Magazine Style — Serif + Sans

- **Heading**: Libre Bodoni
- **Body**: Public Sans
- **Mood**: magazine, editorial, publishing, refined, journalism, print
- **Best for**: Magazines, online publications, editorial content, journalism
- **Note**: Bodoni's editorial elegance. Public Sans for clean UI.

```css
@import url('https://fonts.googleapis.com/css2?family=Libre+Bodoni:wght@400;500;600;700&family=Public+Sans:wght@300;400;500;600;700&display=swap');
```

```js
fontFamily: { serif: ['Libre Bodoni', 'serif'], sans: ['Public Sans', 'sans-serif'] }
```

## Crypto/Web3 — Sans + Sans

- **Heading**: Orbitron
- **Body**: Exo 2
- **Mood**: crypto, web3, futuristic, tech, blockchain, digital
- **Best for**: Crypto platforms, NFT, blockchain, web3, futuristic tech
- **Note**: Orbitron for futuristic headers. Exo 2 for readable body.

```css
@import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@300;400;500;600;700&family=Orbitron:wght@400;500;600;700&display=swap');
```

```js
fontFamily: { display: ['Orbitron', 'sans-serif'], body: ['Exo 2', 'sans-serif'] }
```

## Gaming Bold — Display + Sans

- **Heading**: Russo One
- **Body**: Chakra Petch
- **Mood**: gaming, bold, action, esports, competitive, energetic
- **Best for**: Gaming, esports, action games, competitive sports, entertainment
- **Note**: Russo One for impact. Chakra Petch for techy body text.

```css
@import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@300;400;500;600;700&family=Russo+One&display=swap');
```

```js
fontFamily: { display: ['Russo One', 'sans-serif'], body: ['Chakra Petch', 'sans-serif'] }
```

## Indie/Craft — Display + Sans

- **Heading**: Amatic SC
- **Body**: Cabin
- **Mood**: indie, craft, handmade, artisan, organic, creative
- **Best for**: Craft brands, indie products, artisan, handmade, organic products
- **Note**: Amatic for handwritten feel. Cabin for readable body.

```css
@import url('https://fonts.googleapis.com/css2?family=Amatic+SC:wght@400;700&family=Cabin:wght@400;500;600;700&display=swap');
```

```js
fontFamily: { display: ['Amatic SC', 'sans-serif'], sans: ['Cabin', 'sans-serif'] }
```

## Startup Bold — Sans + Sans

- **Heading**: Clash Display
- **Body**: Satoshi
- **Mood**: startup, bold, modern, innovative, confident, dynamic
- **Best for**: Startups, pitch decks, product launches, bold brands
- **Note**: Note: Clash Display on Fontshare. Outfit as Google alternative.

```css
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Rubik:wght@300;400;500;600;700&display=swap');
```

```js
fontFamily: { heading: ['Outfit', 'sans-serif'], body: ['Rubik', 'sans-serif'] }
```

## E-commerce Clean — Sans + Sans

- **Heading**: Rubik
- **Body**: Nunito Sans
- **Mood**: ecommerce, clean, shopping, product, retail, conversion
- **Best for**: E-commerce, online stores, product pages, retail, shopping
- **Note**: Clean readable fonts perfect for product descriptions.

```css
@import url('https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@300;400;500;600;700&family=Rubik:wght@300;400;500;600;700&display=swap');
```

```js
fontFamily: { heading: ['Rubik', 'sans-serif'], body: ['Nunito Sans', 'sans-serif'] }
```

## Academic/Research — Serif + Sans

- **Heading**: Crimson Pro
- **Body**: Atkinson Hyperlegible
- **Mood**: academic, research, scholarly, accessible, readable, educational
- **Best for**: Universities, research papers, academic journals, educational
- **Note**: Crimson for scholarly headlines. Atkinson for accessibility.

```css
@import url('https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Crimson+Pro:wght@400;500;600;700&display=swap');
```

```js
fontFamily: { serif: ['Crimson Pro', 'serif'], sans: ['Atkinson Hyperlegible', 'sans-serif'] }
```

## Dashboard Data — Mono + Sans

- **Heading**: Fira Code
- **Body**: Fira Sans
- **Mood**: dashboard, data, analytics, code, technical, precise
- **Best for**: Dashboards, analytics, data visualization, admin panels
- **Note**: Fira family cohesion. Code for data, Sans for labels.

```css
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Fira+Sans:wght@300;400;500;600;700&display=swap');
```

```js
fontFamily: { mono: ['Fira Code', 'monospace'], sans: ['Fira Sans', 'sans-serif'] }
```

## Music/Entertainment — Display + Sans

- **Heading**: Righteous
- **Body**: Poppins
- **Mood**: music, entertainment, fun, energetic, bold, performance
- **Best for**: Music platforms, entertainment, events, festivals, performers
- **Note**: Righteous for bold entertainment headers. Poppins for body.

```css
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Righteous&display=swap');
```

```js
fontFamily: { display: ['Righteous', 'sans-serif'], sans: ['Poppins', 'sans-serif'] }
```

## Minimalist Portfolio — Sans + Sans

- **Heading**: Archivo
- **Body**: Space Grotesk
- **Mood**: minimal, portfolio, designer, creative, clean, artistic
- **Best for**: Design portfolios, creative professionals, minimalist brands
- **Note**: Space Grotesk for distinctive headers. Archivo for clean body.

```css
@import url('https://fonts.googleapis.com/css2?family=Archivo:wght@300;400;500;600;700&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
```

```js
fontFamily: { heading: ['Space Grotesk', 'sans-serif'], body: ['Archivo', 'sans-serif'] }
```

## Kids/Education — Display + Sans

- **Heading**: Baloo 2
- **Body**: Comic Neue
- **Mood**: kids, education, playful, friendly, colorful, learning
- **Best for**: Children's apps, educational games, kid-friendly content
- **Note**: Fun, playful fonts for children. Comic Neue is readable comic style.

```css
@import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@400;500;600;700&family=Comic+Neue:wght@300;400;700&display=swap');
```

```js
fontFamily: { display: ['Baloo 2', 'sans-serif'], sans: ['Comic Neue', 'sans-serif'] }
```

## Wedding/Romance — Script + Serif

- **Heading**: Great Vibes
- **Body**: Cormorant Infant
- **Mood**: wedding, romance, elegant, script, invitation, feminine
- **Best for**: Wedding sites, invitations, romantic brands, bridal
- **Note**: Great Vibes for elegant accents. Cormorant for readable text.

```css
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Infant:wght@300;400;500;600;700&family=Great+Vibes&display=swap');
```

```js
fontFamily: { script: ['Great Vibes', 'cursive'], serif: ['Cormorant Infant', 'serif'] }
```

## Science/Tech — Sans + Sans

- **Heading**: Exo
- **Body**: Roboto Mono
- **Mood**: science, technology, research, data, futuristic, precise
- **Best for**: Science, research, tech documentation, data-heavy sites
- **Note**: Exo for modern tech feel. Roboto Mono for code/data.

```css
@import url('https://fonts.googleapis.com/css2?family=Exo:wght@300;400;500;600;700&family=Roboto+Mono:wght@300;400;500;700&display=swap');
```

```js
fontFamily: { sans: ['Exo', 'sans-serif'], mono: ['Roboto Mono', 'monospace'] }
```

## Accessibility First — Sans + Sans

- **Heading**: Atkinson Hyperlegible
- **Body**: Atkinson Hyperlegible
- **Mood**: accessible, readable, inclusive, WCAG, dyslexia-friendly, clear
- **Best for**: Accessibility-critical sites, government, healthcare, inclusive design
- **Note**: Designed for maximum legibility. Excellent for accessibility.

```css
@import url('https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&display=swap');
```

```js
fontFamily: { sans: ['Atkinson Hyperlegible', 'sans-serif'] }
```

## Sports/Fitness — Sans + Sans

- **Heading**: Barlow Condensed
- **Body**: Barlow
- **Mood**: sports, fitness, athletic, energetic, condensed, action
- **Best for**: Sports, fitness, gyms, athletic brands, competition
- **Note**: Condensed for impact headlines. Regular Barlow for body.

```css
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;500;600;700&family=Barlow:wght@300;400;500;600;700&display=swap');
```

```js
fontFamily: { display: ['Barlow Condensed', 'sans-serif'], body: ['Barlow', 'sans-serif'] }
```

## Luxury Minimalist — Serif + Sans

- **Heading**: Bodoni Moda
- **Body**: Jost
- **Mood**: luxury, minimalist, high-end, sophisticated, refined, premium
- **Best for**: Luxury minimalist brands, high-end fashion, premium products
- **Note**: Bodoni's high contrast elegance. Jost for geometric body.

```css
@import url('https://fonts.googleapis.com/css2?family=Bodoni+Moda:wght@400;500;600;700&family=Jost:wght@300;400;500;600;700&display=swap');
```

```js
fontFamily: { serif: ['Bodoni Moda', 'serif'], sans: ['Jost', 'sans-serif'] }
```

## Tech/HUD Mono — Mono + Mono

- **Heading**: Share Tech Mono
- **Body**: Fira Code
- **Mood**: tech, futuristic, hud, sci-fi, data, monospaced, precise
- **Best for**: Sci-fi interfaces, developer tools, cybersecurity, dashboards
- **Note**: Share Tech Mono has that classic sci-fi look.

```css
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;400;500;600;700&family=Share+Tech+Mono&display=swap');
```

```js
fontFamily: { hud: ['Share Tech Mono', 'monospace'], code: ['Fira Code', 'monospace'] }
```

## Pixel Retro — Display + Sans

- **Heading**: Press Start 2P
- **Body**: VT323
- **Mood**: pixel, retro, gaming, 8-bit, nostalgic, arcade
- **Best for**: Pixel art games, retro websites, creative portfolios
- **Note**: Press Start 2P is very wide/large. VT323 is better for body text.

```css
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323&display=swap');
```

```js
fontFamily: { pixel: ['Press Start 2P', 'cursive'], terminal: ['VT323', 'monospace'] }
```

## Neubrutalist Bold — Display + Sans

- **Heading**: Lexend Mega
- **Body**: Public Sans
- **Mood**: bold, neubrutalist, loud, strong, geometric, quirky
- **Best for**: Neubrutalist designs, Gen Z brands, bold marketing
- **Note**: Lexend Mega has distinct character and variable weight.

```css
@import url('https://fonts.googleapis.com/css2?family=Lexend+Mega:wght@100..900&family=Public+Sans:wght@100..900&display=swap');
```

```js
fontFamily: { mega: ['Lexend Mega', 'sans-serif'], body: ['Public Sans', 'sans-serif'] }
```

## Academic/Archival — Serif + Serif

- **Heading**: EB Garamond
- **Body**: Crimson Text
- **Mood**: academic, old-school, university, research, serious, traditional
- **Best for**: University sites, archives, research papers, history
- **Note**: Classic academic aesthetic. Very legible.

```css
@import url('https://fonts.googleapis.com/css2?family=Crimson+Text:wght@400;600;700&family=EB+Garamond:wght@400;500;600;700;800&display=swap');
```

```js
fontFamily: { classic: ['EB Garamond', 'serif'], text: ['Crimson Text', 'serif'] }
```

## Spatial Clear — Sans + Sans

- **Heading**: Inter
- **Body**: Inter
- **Mood**: spatial, legible, glass, system, clean, neutral
- **Best for**: Spatial computing, AR/VR, glassmorphism interfaces
- **Note**: Optimized for readability on dynamic backgrounds.

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
```

```js
fontFamily: { sans: ['Inter', 'sans-serif'] }
```

## Kinetic Motion — Display + Mono

- **Heading**: Syncopate
- **Body**: Space Mono
- **Mood**: kinetic, motion, futuristic, speed, wide, tech
- **Best for**: Music festivals, automotive, high-energy brands
- **Note**: Syncopate's wide stance works well with motion effects.

```css
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syncopate:wght@400;700&display=swap');
```

```js
fontFamily: { display: ['Syncopate', 'sans-serif'], mono: ['Space Mono', 'monospace'] }
```

## Gen Z Brutal — Display + Sans

- **Heading**: Anton
- **Body**: Epilogue
- **Mood**: brutal, loud, shouty, meme, internet, bold
- **Best for**: Gen Z marketing, streetwear, viral campaigns
- **Note**: Anton is impactful and condensed. Good for stickers/badges.

```css
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Epilogue:wght@400;500;600;700&display=swap');
```

```js
fontFamily: { display: ['Anton', 'sans-serif'], body: ['Epilogue', 'sans-serif'] }
```

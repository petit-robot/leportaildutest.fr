import themeConfig from "./themeConfig"

function getBasePath(): string {
  if (process.env.NODE_ENV === 'development') {
    return 'http://localhost:4321';
  }

  return themeConfig.general.seo.url;
}

export function getOGImage(slug?: string) {
  let basePath: string = getBasePath();

  // Pages without a slug (accueil, 404) have no generated card: use the site logo
  // instead of letting crawlers pick the first image found in the page.
  if (!slug) {
    return `${basePath}${themeConfig.general.logo}`;
  }

  return `${basePath}/og/${slug}.png`;
}
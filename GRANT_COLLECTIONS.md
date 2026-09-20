# Create SEO collections — one approval needed

Blog Autopost can now request **product/collection** scopes (version `blog-autopost-3`).

## 1) Approve scopes (you — ~10 seconds)

While logged into Shopify Admin, open:

https://admin.shopify.com/store/the-pickle-affair/oauth/install?client_id=e47ce2d8e254ca7eaf7a59dee082fd71

Click **Update / Allow** for `read_products` + `write_products`.

Or: **Settings → Apps → Blog Autopost → Update** if Shopify shows a banner.

## 2) Create the 8 collections (automatic)

After approval, say **“collections approved”** or run:

```bash
gh workflow run "Create SEO Collections" --repo arhamtechnology3-beep/thepickleaffairblogAutopost
```

Creates/updates (from `COLLECTIONS_SEO_PLAN.md`):

| Collection | URL |
|---|---|
| All Mango Pickles | `/collections/all-mango-pickles` |
| Sweet Gujarati Pickles | `/collections/sweet-gujarati-pickles` |
| Spicy & Traditional Keri Achar | `/collections/spicy-traditional-keri-achar` |
| Gunda Keri & Specialty Achar | `/collections/gunda-keri-specialty-achar` |
| Methi / Fenugreek Pickles | `/collections/methi-fenugreek-pickles` |
| Kathiawadi Homemade Pickles | `/collections/kathiawadi-homemade-pickles` |
| Pickles for Thepla & Tiffin | `/collections/pickles-for-thepla-tiffin` |
| Buy Gujarati Pickle Online | `/collections/buy-gujarati-pickle-online` |

## Already done

- Footer SHOP links point at these URLs (live theme `#152681250967`)
- Creator script + GitHub Action ready

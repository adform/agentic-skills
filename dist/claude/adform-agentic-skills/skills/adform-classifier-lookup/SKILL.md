---
name: adform-classifier-lookup
description: Look up Adform classifier IDs (geo, network, device, content, and mobile reference data) by name via the Adform GraphQL MCP. Covers continents, countries, regions, cities, DMA regions, zip codes, ISPs, languages, locale languages, browsers, device types, device properties, operating systems, display resolutions, bandwidths, IAB categories, industry verticals, time zones, mobile carriers, and mobile apps/categories/stores. Use whenever a classifier ID is needed for targeting, filtering, forecasting inputs, or campaign/line item setup. Trigger on "find [classifier] ID", "look up classifier", "resolve [name] to ID", "what's the ID for X".
---
# Adform Classifier Lookup
Adform's targeting, forecasting, and reporting inputs reference classifiers by numeric `id` (or, for a few, by `code`/`name`) rather than by free text. Every classifier query follows the same shape: a plural query takes a `search` string (or a `searchFilter` input for a few of them) and returns a list wrapper with the matching entities plus `totalCount`.

## General pattern
```graphql
query ClassifierLookup {
  <classifierQuery>(search: "<name>") {
    <pluralField> {
      id
      name
      # ...classifier-specific fields
    }
    totalCount
  }
}
```
Swap `<classifierQuery>` / `<pluralField>` for the ones in the table below, and replace `search` with the name fragment you're resolving.

## Classifier reference

| Domain | Query | Filters | Wrapper field | Returns | Notes |
|---|---|---|---|---|---|
| Continent | `continents` / `continent(id)` | search | `continents` | `id, code, name` | |
| Country | `countries` / `countrySearch` / `country(id)` | search, continentId | `countries` | `id, continentId, name, iso3Code, iso2Code` | |
| Region | `regions` / `regionSearch` / `region(id)` | search, countryId | `regions` | `id, name, code, countryId` | |
| City | `cities` / `citySearch` / `city(id)` | search, countryId, regionId | `cities` | `id, name, countryId, regionId` | |
| DMA Region | `dmaRegions` / `dmaRegionSearch` / `dmaRegion(id)` | search, countryId | `dmaRegions` | `id, name, countryId` | US-style designated market areas |
| Zip code | `zipCodes` / `zipCodeSearch` / `zipCode(id)` | search, code, cityId, regionId, countryId | `zipCodes` | `id, code, cityId, regionId, countryId, dmaRegionId` | |
| ISP | `isps` / `ispSearch` / `isp(id)` | search, isActive | `isps` | `id, name, active` | |
| Language | `languages` / `language(code)` | search | `languages` | `code, name` | Keyed by culture code (e.g. `en-US`), not numeric id |
| Locale language | `localeLanguages` / `localeLanguage(id)` | search | `localeLanguages` | `id, name` | |
| Browser | `browsers` / `browser(id)` | search | `browsers` | `id, name` | |
| Device type | `deviceTypes` / `deviceType(id)` | search | `deviceTypes` | `id, name` | |
| Device property | `deviceProperties` / `devicePropertySearch` | search, types (`platform/deviceType/deviceVendor/deviceModel/browser`), statuses | `deviceProperties` | `type, id, name, active` | One query across all device-property facets |
| Operating system | `operatingSystems` / `operatingSystem(id)` | search, ids, includeInactive | `operatingSystems` | `id, name, deviceTypeId` | |
| Display resolution | `displayResolutions` / `displayResolution(id)` | search | `displayResolutions` | `id, name` | |
| Bandwidth | `bandwidths` / `bandwidth(id)` | search | `bandwidths` | `id, name` | |
| IAB category | `iabCategorySearch` / `iabCategory(id)` | searchFilter `{ids, name}` | `iabCategories` | `id, name, code, parentId` | No plain-string `search` arg. Use `searchFilter: {name: "..."}` |
| Industry vertical | `industryVerticals` | none | `industryVerticals` | `name` only | No `id` field at all. Match and pass the name string itself |
| Time zone | `timeZones` | none | *(direct list, no wrapper)* | `name, description` | Full list only, e.g. name `Europe/Berlin` |
| Mobile carrier | `mobileCarrierSearch` / `mobileCarrier(id)` | searchFilter `{ids, name}` | `mobileCarrier` (singular, inconsistent with the rest) | `id, name, countryId` | No plain-string `search` arg |
| Mobile application | `mobileApplications` | search (**required**), source (`active`/`all`) | `applications` | `id, storeId, name, developer` | A search term is mandatory; listing all apps is not supported |
| Mobile category | `mobileCategories` | none | `categories` | `id, name, parentId, storeId` | |
| Mobile store | `mobileStores` | none | `stores` | `id, name` | |

The mixed geo `locations`/`locationSearch` classifier (cross-type search returning city, region, DMA region, or country matches in one call) is out of scope for this iteration and will be added separately once its output can be documented against the classifier namespace above.

## Worked examples

Standard shape (covers most geo, device, and network classifiers):
```graphql
query ClassifierCountries {
  countries(search: "India") {
    countries { id continentId name iso3Code iso2Code }
  }
}
```

Classifiers needing a `searchFilter` input instead of a plain string (IAB category, mobile carrier):
```graphql
query ClassifierMobileCarriers {
  mobileCarrierSearch(searchFilter: { name: "Vodafone" }) {
    mobileCarrier { id name countryId }
    totalCount
  }
}
```

Classifiers with no search parameter: fetch the full list and match client-side (industry vertical, time zone, mobile category/store):
```graphql
query ClassifierIndustryVerticals {
  industryVerticals(limit: 500) {
    industryVerticals { name }
    totalCount
  }
}
```

Mobile application search: `search` is required, so there is no list-everything fallback:
```graphql
query ClassifierMobileApps {
  mobileApplications(search: "Instagram", source: active) {
    applications { id storeId name developer }
    totalCount
  }
}
```

## Notes
- `countryId`, `regionId`, `cityId`, and `dmaRegionId` from these classifiers are identifiers in the classifier namespace. RTB line item location targeting (`RtbLineItemTargetingRules.locations`) uses a separate `locationId` namespace.
- Most geo classifiers (region, city, DMA region, zip code) accept a parent `countryId`/`regionId` to narrow results once you've resolved the country. Resolve top-down (continent, country, region, city) rather than guessing a name match at the lowest level.
- `language` is looked up by culture `code` (e.g. `en-US`), not by a numeric `id`.
- Two naming inconsistencies to watch for: `mobileCarrierSearch` returns a singular `mobileCarrier` wrapper field despite returning a list, and `industryVerticals` has no `id` field. Pass the `name` string directly wherever an industry vertical is expected.
- Always confirm a wrapper's field name with `graphql_introspect` before wiring a new query into a downstream tool. Most follow `<queryName>` pluralized, but not all (see above).

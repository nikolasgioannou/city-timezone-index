# City → Timezone Search Index

Builds a small, fast JSON index for client-side city-to-timezone search.

- Source: GeoNames cities15000.txt
- Includes major cities + all country capitals
- Joins country names
- Normalizes names for easy search
- Uses IANA timezones

Output shape (example):

```json
{
  "id": "uuid",
  "city": "São Paulo",
  "country": "Brazil",
  "timezone": "America/Sao_Paulo",
  "search": "brazil sao paulo são paulo"
}
```

Output file:

```
cities100000_with_country.json
```

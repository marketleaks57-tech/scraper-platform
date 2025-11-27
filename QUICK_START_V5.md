# Quick Start Guide - Scraper Platform v5.0

## Creating a New Scraper (5 Minutes)

### 1. Use the Scaffolding Tool

```bash
python tools/add_scraper_advanced.py my_source \
  --engine selenium \
  --base-url https://example.com \
  --requires-login \
  --interactive
```

This creates:
- ✅ `src/scrapers/my_source/pipeline.py` - Scraper implementation
- ✅ `config/sources/my_source.yaml` - Source configuration
- ✅ `dsl/pipelines/my_source.yaml` - Pipeline definition
- ✅ `dags/scraper_my_source.py` - Airflow DAG (v5)

### 2. Implement Core Functions

Edit `src/scrapers/my_source/pipeline.py`:

```python
def fetch_listings(env=None, **params):
    """Fetch product listing URLs."""
    # Your code here
    return ["url1", "url2", "url3"]

def parse_products(fetch_listings, **params):
    """Parse product details from URLs."""
    urls = fetch_listings  # Output from previous step
    products = []
    for url in urls:
        # Your parsing code
        products.append({"name": "...", "price": "..."})
    return products

def normalize_data(parse_products, **params):
    """Normalize product data."""
    products = parse_products
    # Normalization logic
    return normalized_products

def export_database(normalize_data, **params):
    """Export to database."""
    products = normalize_data
    # Export logic
    return {"item_count": len(products)}
```

### 3. Define Pipeline

Edit `dsl/pipelines/my_source.yaml`:

```yaml
pipeline:
  name: my_source
  description: My source scraper
  
  steps:
    - id: fetch_listings
      component: my_source.fetch_listings
      type: fetch
    
    - id: parse_products
      component: my_source.parse_products
      type: parse
      depends_on:
        - fetch_listings
    
    - id: normalize_data
      component: my_source.normalize
      type: enrich
      depends_on:
        - parse_products
    
    - id: export_db
      component: my_source.export
      type: export
      depends_on:
        - normalize_data
```

### 4. Register Components

Edit `dsl/components.yaml`:

```yaml
components:
  my_source.fetch_listings:
    module: src.scrapers.my_source.pipeline
    callable: fetch_listings
    type: fetch
    
  my_source.parse_products:
    module: src.scrapers.my_source.pipeline
    callable: parse_products
    type: parse
    
  my_source.normalize:
    module: src.scrapers.my_source.pipeline
    callable: normalize_data
    type: enrich
    
  my_source.export:
    module: src.scrapers.my_source.pipeline
    callable: export_database
    type: export
```

### 5. Test Locally

```bash
# Test pipeline
python -m src.entrypoints.run_pipeline \
  --source my_source \
  --environment dev \
  --run-type FULL_REFRESH

# Check Airflow DAG
airflow dags test scraper_my_source_v5 2024-11-27
```

## Running Existing Scrapers

### From Command Line

```bash
# Dev environment
python -m src.entrypoints.run_pipeline --source alfabeta --environment dev

# Production
python -m src.entrypoints.run_pipeline --source alfabeta --environment prod --run-type FULL_REFRESH
```

### From Airflow UI

1. Navigate to `http://localhost:8080` (or your Airflow URL)
2. Find DAG: `scraper_alfabeta_v5`
3. Click "Trigger DAG"
4. (Optional) Add configuration:
   ```json
   {
     "run_type": "FULL_REFRESH",
     "environment": "prod",
     "params": {}
   }
   ```

### From Jira

Create issue with labels:
- `scraper:alfabeta`
- `run_type:FULL_REFRESH`
- `environment:prod`

Webhook triggers DAG automatically.

## Common Patterns

### Step with Retry

```yaml
steps:
  - id: fetch_data
    component: my_source.fetch
    type: fetch
    retry: 3  # Retry up to 3 times
    timeout: 60  # 60 second timeout
```

### Optional Step

```yaml
steps:
  - id: optional_validation
    component: my_source.validate
    type: validate
    required: false  # Won't fail pipeline if it fails
```

### Parallel Steps

Dependencies automatically parallelized:

```yaml
steps:
  - id: fetch_category_a
    component: my_source.fetch_a
    type: fetch
  
  - id: fetch_category_b
    component: my_source.fetch_b
    type: fetch
  
  # These run in parallel (no dependencies between them)
  
  - id: merge_results
    component: my_source.merge
    type: transform
    depends_on:
      - fetch_category_a
      - fetch_category_b
```

### Sequential Exports

Export steps automatically run sequentially:

```yaml
steps:
  - id: export_db
    component: my_source.export_db
    type: export  # Runs first
  
  - id: export_s3
    component: my_source.export_s3
    type: export  # Runs after export_db
  
  # No need to specify depends_on!
```

## Configuration

### Source Config: `config/sources/my_source.yaml`

```yaml
base_url: https://example.com
login_url: https://example.com/login
require_login: true

selectors:
  product_title: ".product-name"
  price: ".price"
  
options:
  max_pages: 10
  delay_between_requests: 1.0
```

### Environment Config: `config/env/dev.yaml`

```yaml
database:
  host: localhost
  port: 5432
  name: scraper_dev

s3:
  bucket: scraper-dev-bucket
  region: us-east-1
```

## Troubleshooting

### Pipeline Not Found

```
Error: Pipeline file not found
```

**Solution**: Create `dsl/pipelines/{source}.yaml`

### Component Not Registered

```
Error: Component 'my_source.fetch' not registered
```

**Solution**: Add to `dsl/components.yaml`

### Import Error

```
ImportError: cannot import name 'fetch_listings'
```

**Solution**: 
1. Check function exists in module
2. Verify module path is correct
3. Test import: `python -c "from src.scrapers.my_source.pipeline import fetch_listings"`

### Dependency Error

```
RuntimeError: Pipeline deadlock detected
```

**Solution**:
1. Check `depends_on` references valid step IDs
2. Ensure no circular dependencies
3. Verify all dependencies are defined

## Advanced Features

### Custom Step Type

```python
from src.pipeline.step import StepType, PipelineStep

# In your pipeline definition
step = PipelineStep(
    id="custom_operation",
    type=StepType.CUSTOM,
    callable=my_custom_function,
    params={"param1": "value1"},
)
```

### Dynamic Parameters

```python
def my_step(env=None, run_type=None, **params):
    """Step that uses runtime parameters."""
    if env == "dev":
        # Dev behavior
        pass
    elif run_type == "DELTA":
        # Delta run behavior
        pass
    
    # Access custom params
    max_items = params.get("max_items", 100)
```

### Context Passing

```python
def step1(**params):
    """First step returns data."""
    return {"products": [...], "metadata": {...}}

def step2(step1, **params):
    """Second step receives step1 output."""
    products = step1["products"]
    metadata = step1["metadata"]
    # Process...
    return processed_products
```

## Best Practices

### 1. Keep Steps Small and Focused
```python
# ✅ Good
def fetch_listings():
    """Only fetches listings."""
    return urls

def parse_products(fetch_listings):
    """Only parses products."""
    return products

# ❌ Bad
def fetch_and_parse_everything():
    """Does too much."""
    # ...hundreds of lines...
```

### 2. Use Type Hints
```python
from typing import List, Dict, Any

def fetch_listings(env: str = None) -> List[str]:
    """Fetch product listing URLs."""
    return urls

def parse_products(fetch_listings: List[str]) -> List[Dict[str, Any]]:
    """Parse products from URLs."""
    return products
```

### 3. Handle Errors Gracefully
```python
def fetch_listings(**params):
    """Fetch with error handling."""
    try:
        urls = scrape_urls()
        return urls
    except ConnectionError as exc:
        log.error("Failed to fetch listings: %s", exc)
        raise  # Re-raise for retry logic
```

### 4. Log Important Events
```python
from src.common.logging_utils import get_logger

log = get_logger("my_source")

def fetch_listings(**params):
    log.info("Starting fetch for my_source")
    urls = scrape_urls()
    log.info("Fetched %d URLs", len(urls))
    return urls
```

### 5. Document Your Steps
```python
def normalize_data(parse_products, **params):
    """Normalize product data to standard schema.
    
    Args:
        parse_products: Raw product data from parser
        **params: Runtime parameters (env, run_type, etc.)
        
    Returns:
        List of normalized product dictionaries
        
    Raises:
        ValidationError: If product data is invalid
    """
    products = parse_products
    # Normalization logic...
    return normalized
```

## Performance Tips

### 1. Enable Parallel Execution
```python
# In run_pipeline.py or custom runner
runner = PipelineRunner(max_workers=8)  # More workers
```

### 2. Optimize Export Steps
```python
def export_database(normalize_data, **params):
    """Bulk insert for better performance."""
    products = normalize_data
    
    # ✅ Good: Bulk insert
    db.bulk_insert(products)
    
    # ❌ Bad: One-by-one
    for product in products:
        db.insert(product)
```

### 3. Use Caching
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def lookup_pcid(product_name: str) -> str:
    """Cached PCID lookup."""
    return db.query_pcid(product_name)
```

## Next Steps

1. **Read**: [`ARCHITECTURE_V5.md`](ARCHITECTURE_V5.md) for deep dive
2. **Explore**: Example scrapers in `src/scrapers/`
3. **Test**: Run existing scrapers locally
4. **Create**: Build your first scraper
5. **Deploy**: Push to production

## Questions?

- Check [`ARCHITECTURE_V5.md`](ARCHITECTURE_V5.md)
- Review [`CLEANUP_SUMMARY.md`](CLEANUP_SUMMARY.md)
- Look at test examples in `tests/`
- Check existing scrapers for patterns

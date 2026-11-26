# Setup guide

## Part A: Upload to GitHub
Create a **public**, empty repository named `azure-databricks-customer-cdc-pipeline`
(no README, .gitignore or license). Unzip the project, open a terminal inside it and run:
```bash
git init
git add .
git commit -m "Add customer CDC pipeline"
git branch -M main
git remote add origin https://github.com/<your-username>/azure-databricks-customer-cdc-pipeline.git
git push -u origin main
```
Then open the **Actions** tab and check the **CI** result.

## Part B: Run in Databricks
Use an Azure Databricks workspace with Unity Catalog and serverless pipelines, or
Databricks Free Edition. Free Edition has usage limits, allows one active pipeline per
pipeline type and is for non-commercial use. On Azure, check costs first.
Menu names can change between releases.

1. **Workspace > Create > Git folder**, then paste your repository URL.
2. Open `notebooks/00_setup`, keep `batch = 1` and run all.
   Copy the `landing_path` printed at the end.
   On Azure, set `catalog` to one you can use (`SHOW CATALOGS`).
3. In **Jobs & Pipelines**, create an **ETL pipeline** and choose to use existing code:
   - Root folder: the `pipeline` folder of your Git folder
   - Source code: `pipeline/transformations`
4. In the pipeline settings:
   - Default catalog: `workspace` (or yours). Default schema: `customer_cdc`
   - Compute: serverless
   - Add a configuration entry. Key: `landing_path`. Value: the path from step 2
5. Run **Dry run** to check the code, then **Run pipeline**.
6. Run `notebooks/01_validate_results` and compare the counts with the README.
7. Run `00_setup` with `batch = 2`, run the pipeline again, then validate again.
   Use a normal update, not a full refresh.
8. Run `sql/business_queries.sql` in the SQL editor.

## Part C: Deploy with a bundle (alternative to steps 3 to 5, optional)
Needs a current Databricks CLI.
```bash
databricks auth login --host https://<your-workspace-url>
databricks bundle validate
databricks bundle deploy -t dev
databricks bundle run customer_cdc_job -t dev
databricks bundle run customer_cdc_job -t dev --params batch=2
```
Use either the manual pipeline or the bundle for a schema, not both: two pipelines cannot
manage the same tables. For another catalog, add `--var="catalog=<name>"`.

## Part D: Add proof of your run
Save screenshots of the pipeline graph, the expectation metrics and the `C001` history
query in `docs/images`. Hide your email and workspace URL, link them in the README,
then commit and push.

## Clean up
Delete the pipeline first (or run `databricks bundle destroy -t dev`). Then, only if you
want to **delete all remaining data and files in this project schema**:
```sql
DROP SCHEMA IF EXISTS workspace.customer_cdc CASCADE;
```

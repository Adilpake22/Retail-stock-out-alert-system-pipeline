# processing/validate.py
import great_expectations as gx

def validate_inventory(df):
    context = gx.get_context()
    ds = context.sources.add_or_update_pandas("inventory_source")
    da = ds.add_dataframe_asset("inventory_df", dataframe=df.to_pandas())
    batch = da.build_batch_request()

    suite = context.add_or_update_expectation_suite("inventory_suite")
    validator = context.get_validator(batch_request=batch,
                                      expectation_suite=suite)

    validator.expect_column_values_to_not_be_null("product_id")
    validator.expect_column_values_to_not_be_null("stock_qty")
    validator.expect_column_values_to_be_between("stock_qty", 0, 100000)
    validator.expect_column_values_to_be_between("daily_sales", 0, 10000)

    result = validator.validate()
    if not result["success"]:
        raise ValueError(f"Data validation failed: {result}")
    print("✅ Data validation passed")
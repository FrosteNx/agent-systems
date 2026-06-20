def save_dataframe(df, path, index=False, index_label=None):
    df.to_csv(
        path,
        index=index,
        index_label=index_label
    )
    print(f"Saved: {path}")
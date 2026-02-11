def retention_ratio(common, baseline):
    if baseline == 0:
        return 0
    return common / baseline

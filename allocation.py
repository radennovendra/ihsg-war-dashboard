def pick_sector_champions(results, top_sectors, max_per_sector=2):
    champions = []

    for sec in top_sectors:
        sector_stocks = [x for x in results if x[1]["sector"] == sec]
        sector_stocks.sort(key=lambda x: x[1]["score"], reverse=True)

        champions += sector_stocks[:max_per_sector]

    return champions

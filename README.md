# zkb

## Load data from Bloomberg
The folder ```data``` contains the subfolders ```assets_raw``` (data obtained when adjusting the roll with "Ratio"), ```assets_raw_none``` (which is the data obtained when adjusting the roll with "None"), and ```support```, which contain the data that we obtain
from running the three ```.java``` files (in the same folder). We run the scripts on the Bloomberg terminals from the command line with:

```javac -cp ".;C:\Program Files (x86)\blp\dapi\blpapi3.jar" GetData.java``` \
```java -cp ".;C:\Program Files (x86)\blp\dapi\blpapi3.jar" GetData```

```javac -cp ".;C:\Program Files (x86)\blp\dapi\blpapi3.jar" GetDataNone.java``` \
```java -cp ".;C:\Program Files (x86)\blp\dapi\blpapi3.jar" GetDataNone```

```javac -cp ".;C:\Program Files (x86)\blp\dapi\blpapi3.jar" GetSupport.java``` \
```java -cp ".;C:\Program Files (x86)\blp\dapi\blpapi3.jar" GetSupport```


## Prepare Assets
```python prepareAssets.py``` prepares the data for the backtest. Concretly, it loads the data from ```data/assets_raw```, ```data/assets_raw_none```, and ```data/support```, cleans it by excluding certain rows and imputing certain missing values, and converts them all to CHF. It then stores the data in ```data/assets``` and ```data/assets_none```.


## Backtest
All the other Python files starting with ```assetsFinal...``` calculate the results of different backtests.

* The first 4 files (```...Combinations.py```) contain the signal mixing for 2 signals (```assetsFinal2Combinations.py```) and for 3 signals (```assetsFinal2Combinations.py```). Note, that those two always pick 5 assets long and short, thus there is also an "advanced" case, in which 2 signals pick 10 assets (```assetsFinalAdv2Combinations.py```) and 3 signals pick 15 assets (```assetsFinalAdv3Combinations.py```). The "advanced" codes are only applied to multi-asset cases, because we do not have enough assets in the individual asset categories.
* All other files follow the same logic, such that they essentially only differ in the assets that they use (indicated by the name; see ```class All_assets```) and the location they store their results in (see corresponding ```results_FINAL_...``` folder). The names are self explaining, excpet ```partialCommodity``` and ```partialCommodity2```, which only contain "crude oil, heating oil, and gold" respectively "crude oil and gold". Note, that it would be a simple task to combine all of these files together - due to reproducibility and parallelization reasons we kept them individual.

In each ```results_FINAL_...``` folder we have different subfolders and ```.csv``` files. The ```.csv``` files directly in the folder can be ignored, because we just stored all the data, calculated returns, and calculated signals, such that we can manually check & dive into the code's result. Of interest is the ```backtest_summary_FINAL_....``` file and the subfolder ```trades``` which contain, FOR each trading strategy of interest, the average return (not annualized) respectively the actual trades. The ```results_FINAL_...``` folder also contains the subfolders ```baseline 2``` and ```baseline 3``` (and when applicable subfolders ```adv_baseline 2``` and ```adv_baseline 3```). These ```baseline...``` folders contain the signal mixing from the ```...Combinations.py``` files.

Lastly, the strategy names warrant some explanation:
* 1) Name of the assets included in this strategy (sometimes it is dropped, due to length constraints)
* 2) ```adj``` risk adjusts the signal by the assets volatility; ```basic``` does not risk adjustment
* 3) Exact strategy name
* 4) Trading period - always weekly
* 5) ```weekly``` gives all assets in the legs the same weighting (i.e., usually 20%); ```vola``` introduces risk weighting based on the assets volatility (i.e., 1/vola)
* 6) ```ratio``` uses the ratio-adjusted prices to compute the signal, risk adjustment & risk weighting; ```none``` uses the none-adjusted prices (return is still calculated on the ratio-adjusted prices)
* 7) defines whether we have the data, returns, signals or trades (of interest are usually the trades).

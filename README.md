# An asynchronized api server for opinion_aen (aspect based sentiment analysis)

## installation
```bash
docker build -t NAME . --no-cache
docker run NAME
```

## How to use?
```bash
curl -X POST -H "Content-Type: application/json" -d '{"data":[{"target":"WORD", "context":"SENTENCE"}], "batch_size":100}' 'http://YOUR_IP:1600/predict'
```
Given the target (sentiment to be analyzed) and the sentence which the target is among.

The output of API will be
```json
{
	"data":[{"target":["经济"], "context":["这一年因全球流行病以及各国关系不稳定, 使得经济状况不佳, 但股市经过一个下修后已经回升甚至创新高"]}, ...],
	"polar":[1, ...],
	"prob":[[0.035, 0.79, 0.175], ...],
	"t2":[1603424965.35, ...],
	"t3":[1603424983.12, ...]
	
}
```
Batch input -> batch output

For each data:

	data(dict): raw input

	polar(int): sentiment class. 0-negative, 1-neural, 2-positive.

	prob(list): probability for each sentiment class.

	t2(float): start time of prediction

	t3(float): end time of prediction


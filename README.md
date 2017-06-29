# scarplet-python
Python framework for template matching to detect fault scarps in ALSM data

## Changelog

Date            | Description
--------------- | -----------
23-24 June 2017 | Start framework for worker management and autoscaling
22 June 2017    | Finished implementing basic parallel grid search functionality 
15 May 2017     | Added download utility for OpenTopography data
12 May 2017     | Template and parameter search pass synthetic tests

## TODO

- Test and time multiple instances with task-specific queues
- Processing time estimate
- Get AWS autoscaling working
- AWS testing
- ~~Test with Carrizo data~~
- ~~Test AWS "search and gather" chord~~ Doesn't work: don't send data in backend messages...
- ~~Write gather and compare task~~

## Notes
### Using `celery` and `boto`
- `waiting()` and `complete_count()` method calls can be expensive
- group methods can't track progress if `ignore_result=True`...

### Running workers
- **One worker per queue**
- Queue up tasks, then launch workers: better chance of consuming tasks sitting on queue?
- Use `celery --autoscale=min,max` to limit concurrent jobs (best with concurrency at least # processors)
- Running multiple workers on one machine doesn't seem to make a difference in how jobs are consumed

### Observations...
- Run time constrained by I/O: Pickling/un-pickling
- Run time constraiend by CPU: Matching template
- Memory not a limiting factor for `t2.medium` or better (maybe `t2.small` too?) 
- `t2.micro` instances run out of memory on 8 MB Carrizo test case (duh)

## Benchmark list

**Parameters:** *dkt* = 0.1, *kt* max = 10^3.5, orientation -90/+90

Test case             | Platform                                 | Time
:-------------------- | :--------------------------------------- | ---------:
Synthetic (200 x 200) | Laptop (using 1/4 2.5 GHz CPU, 4 GB RAM) |  
"                     | AWS (5 x *t2.xlarge* instances)          | 
"                     | AWS                                      | 
Synthetic (400 x 400) | Laptop                                   |  
"                     | AWS                                      | 
"                     | AWS                                      | 
Carrizo (~500 x 4000) | Laptop                                   | 3.6 hrs 
"                     | AWS: Fit on instances, compare on laptop | ~1 hr (62 min) 
"                     | AWS: Fit and compare on instances        | ~0.52 hr (31 min) 
"                     | AWS: Single-search step granularity      | > 13 hrs

**Parameters:** *dkt* = 0.25, *kt* max = 10^3.5, orientation -90/+90

Test case             | Platform                                 | Time
:-------------------- | :--------------------------------------- | ---------:
Synthetic (200 x 200) | Laptop (using 1/4 2.5 GHz CPU, 4 GB RAM) |  
"                     | AWS                                      | 
"                     | AWS                                      | 
Synthetic (400 x 400) | Laptop                                   |  
"                     | AWS                                      | 
"                     | AWS                                      | 
Carrizo (~500 x 4000) | Laptop                                   | 1.4 hrs (85 min)
"                     | AWS Fit on instances, compare on laptop  | 20 min
"                     | AWS                                      | 




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

- Test with Carrizo data
- ~~Test AWS "search and gather" chord~~ Doesn't work: don't send data in backend messages...
- Write gather and compare task
- Get AWS autoscaling working
- AWS testing
- Processing time estimate

## Notes
### Using `celery` and `boto`
- `waiting()` and `complete_count()` method calls can be expensive
- group methods can't track progress if `ignore_result=True`...

### Running workers
- Use `celery --autoscale=min,max` to limit concurrent jobs (best with concurrency at least # processors)
- Running multiple workers on one machine doesn't seem to make a difference in how jobs are consumed

### Observations...
- Run time constrained by I/O: Pickling/un-pickling
- Run time constraiend by CPU: Matching template
- Memory not a limiting factor for `t2.medium` or better (maybe `t2.small` too?) 
- `t2.micro` instances run out of memory on 8 MB Carrizo test case (duh)

## Benchmark list
Test case             | Platform                                 | Time
--------------------- | ---------------------------------------- | ---------
Synthetic (200 x 200) | Laptop (using 1/4 2.5 GHz CPU, 4 GB RAM) | c
s                      | AWS (5 x *t2.xlarge* instances)          |c
r                      | AWS (5 x *t2.xlarge* instances)          |c
Synthetic (400 x 400) | Laptop                                   | c
 r                     | AWS (5 x *t2.xlarge* instances)          |c
  f                    | AWS (5 x *t2.xlarge* instances)          |c
Carrizo (~500 x 4000) | Laptop                                   | 4-6 hrs? 
                d      | AWS (5 x *t2.xlarge* instances)          |c
               v       | AWS (5 x *t2.xlarge* instances)          |c

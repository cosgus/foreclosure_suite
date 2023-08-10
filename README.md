Foreclosure Suite - A project that scrapes and models data from Miami-Dade foreclosure pipeline to give investors some forward guidance

This repo is a portfolio piece and a refactor of my original codebase. The original code is currently visible in the deprecated folder

This project was originally designed to create a filter on upcoming foreclosure auctions. When I
first started writing this code back in 2015 there were often days that had over 100 foreclosure auctions.
Buying a property at foreclosure requires a significant amount of due diligence and it was simply not possible to
adequately research all of the auctions. 

Foreclosure suite uses modeling to filter out auctions that are not likely worth researching. The models assess three criteria
to determine if a property is worth researching.

1 - How likely is it that the auction will be canceled prior to the sale date
2 - How likely is it that the Plaintiff will make the winning bid
3 - Given the property is sold to a 3rd party, how much will it sell for



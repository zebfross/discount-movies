var express = require('express');
var db = require('../db');
var router = express.Router();
var hbs = require('hbs');

function percentDiscount(price) {
  if (price.isOnSale && price.originalAmount != 0)
      return 1 - (price.amount / price.originalAmount)
  return 0
}

function formatPercent(amount) {
  if(amount != undefined && amount['amount'] != undefined)
    return amount['amount'].toFixed(0) + "%";
  return "";
}

function formatCurrency(amount) {
  if(amount != undefined && amount['amount'] != undefined)
    return '$' + amount['amount'].toFixed(0);
  return "";
}

function biggestBuyDiscount(prices) {
  var discount = 0;
  var bestPrice = {};
  prices.forEach((price) => {
      if (price['priceType'].match(/Buy( )?/) && percentDiscount(price) > discount) {
          discount = percentDiscount(price);
          bestPrice = price;
      }
  });

  return bestPrice;
}

function biggestRentDiscount(prices) {
  var discount = 0;
  var bestPrice = {};
  prices.forEach((price) => {
      if (!price['priceType'].match(/Buy( )?/) && percentDiscount(price) > discount) {
          discount = percentDiscount(price);
          bestPrice = price;
      }

  });

  return bestPrice;
}

hbs.registerHelper('percentDiscount', percentDiscount);
hbs.registerHelper('biggestRentDiscount', biggestRentDiscount);

hbs.registerHelper('biggestBuyDiscount', biggestBuyDiscount);

hbs.registerHelper('formatCurrency', formatCurrency);
hbs.registerHelper('formatPercent', formatPercent);
hbs.registerHelper('bestBuyAsPercent', function(prices) {return formatPercent(biggestBuyDiscount(prices));});
hbs.registerHelper('bestRentAsPercent', function(prices) {return formatPercent(biggestRentDiscount(prices));});
hbs.registerHelper('asString', function(obj) {return JSON.stringify(obj);})


/* GET home page. */
router.get('/', function(req, res, next) {
  var moviesCollection = db.get().collection('movies');
  moviesCollection.find().toArray(function(err, movies) {
    res.render('index', { 
      title: 'Discount Movies', 
      movies: movies });
  });
});

module.exports = router;

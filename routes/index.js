var express = require('express');
var db = require('../db');
var router = express.Router();
var hbs = require('hbs');

function percentDiscount(price) {
  if (price != undefined && price.isOnSale && price.originalAmount != undefined && price.originalAmount > 0)
      return 1 - (price.amount / price.originalAmount)
  return 0
}

function formatPercent(amount) {
  if(amount != undefined)
    return (amount * 100).toFixed(0) + "%";
  return "-%";
}

function formatCurrency(amount) {
  if(amount != undefined)
    return '$' + amount.toFixed(0);
  return "$-";
}

function formatNumber(amount) {
  if(amount != undefined)
    return '' + amount.toFixed(0);
  return '0';
}

function biggestBuyDiscount(prices) {
  var discount = 0;
  var bestPrice = undefined;
  prices.forEach((price) => {
      if (price['priceType'].match(/Buy( )?/) && percentDiscount(price) >= discount) {
          discount = percentDiscount(price);
          bestPrice = price;
      }
  });

  return bestPrice;
}

function biggestRentDiscount(prices) {
  var discount = 0;
  var bestPrice = undefined;
  prices.forEach((price) => {
      if (price['priceType'].match(/Rent( )?/) && percentDiscount(price) >= discount) {
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
hbs.registerHelper('formatPriceAsCurrency', function(price) {
  if(price != undefined && price['amount'] != undefined)
    return formatCurrency(price['amount']);
  return "$-";
});
hbs.registerHelper('formatPriceAsPercent', function(price) {
  if(price != undefined && price['amount'] != undefined)
    return formatPercent(percentDiscount(price));
  return "-%";
});
hbs.registerHelper('formatPercent', formatPercent);
hbs.registerHelper('formatPriceAsNumber', function(price) {
  if(price != undefined && price['amount'] != undefined)
    return formatNumber(price['amount']);
  return '0';
});
hbs.registerHelper('asString', function(obj) {return JSON.stringify(obj);})


/* GET home page. */
router.get('/', function(req, res, next) {
  var moviesCollection = db.get().collection('movies');
  moviesCollection.find().toArray(function(err, movies) {
    res.render('index', { 
      title: 'Discount Movies', 
      movies: movies,
      flash: req.query.flash});
  });
});

module.exports = router;

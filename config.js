var config = {
    debug: {
        host: "http://localhost:3000",
        db: "@ds028559.mlab.com:28559/discount-movies",
        db_prefix: "test_",
        consoleLog: true
    },
    production: {
        host: "http://stocks.zebfross.com",
        db: "@ds028559.mlab.com:28559/discount-movies",
        db_prefix: "",
        consoleLog: false
    }
}

module.exports = function () {
    if (process.env.ENVIRONMENT == "prod") {
        return config.production
    } else {
        return config.debug
    }
}
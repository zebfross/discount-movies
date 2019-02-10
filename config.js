var config = {
    debug: {
        host: "localhost:3000",
        db: "@ds028559.mlab.com:28559/discount-movies",
        db_prefix: "test_",
        consoleLog: true,
        PORT: 3000,
        mailgun_domain: "sandbox47c93c3b2e5a409c96663306a9320d6f.mailgun.org",
        mailgun_list: "zeb@sandbox47c93c3b2e5a409c96663306a9320d6f.mailgun.org",
        protocol: "http"

    },
    production: {
        host: "movies.zebfross.com",
        db: "@ds028559.mlab.com:28559/discount-movies",
        db_prefix: "",
        consoleLog: false,
        mailgun_domain: "mg.zebfross.com",
        mailgun_list: "",
        protocol: "http"
    }
}

module.exports = function () {
    var settings = config.debug
    if (process.env.ENVIRONMENT == "prod") {
        settings = config.production
    }

    settings["MOVIES_DB_PSWD"] = process.env["MOVIES_DB_PSWD"]
    settings["MOVIES_DB_UNAME"] = process.env["MOVIES_DB_UNAME"]
    settings["ENVIRONMENT"] = process.env["ENVIRONMENT"]
    settings["MAILGUN_KEY"] = process.env["MAILGUN_KEY"]

    return settings
}
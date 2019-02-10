module.exports = function(grunt) {

    // Project configuration.
    grunt.initConfig({
      pkg: grunt.file.readJSON('package.json'),
      exec: {
          testpy: {
              cmd: "py -m unittest discover tests",
              cwd: "C:\\Users\\zebfross\\Documents\\projects\\discount-movies\\azure_function\\.env\\DiscountMovies"
          },
          runpy: {
              cmd: ".\\env\\Scripts\\activate && func host start",
              cwd: "C:\\Users\\zebfross\\Documents\\projects\\discount-movies\\azure_function\\.env\\DiscountMovies"
          }
      },
      env: {
          dev : {
              src : ".env"
          }
      }
    });

    grunt.loadNpmTasks('grunt-exec');
    grunt.loadNpmTasks('grunt-env');
  
    // Register the default tasks.
    grunt.registerTask('test', ['env:dev', 'exec:testpy'])
    grunt.registerTask('run', 'exec:runpy')
    grunt.registerTask('default', ['run']);
    
  };
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
      }
    });

    grunt.loadNpmTasks('grunt-exec');
  
    // Register the default tasks.
    grunt.registerTask('default', ['watch']);
    grunt.registerTask('test', ['exec:testpy'])
    grunt.registerTask('run', 'exec:runpy')
    
  };
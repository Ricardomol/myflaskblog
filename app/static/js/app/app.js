angular.module('blog', [])
  	.config(function($interpolateProvider) {
    	$interpolateProvider.startSymbol('[[');
    	$interpolateProvider.endSymbol(']]');
  	}
);
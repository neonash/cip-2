var app = angular.module('store-directives', []);

app.directive("descriptions", function() {
  return {
    restrict: "E",
    templateUrl: "C:\\Users\\akshat.gupta\\Documents\\atlas-master\\mysite\\atlas\\templates\\comparison\\descriptions.html"
  };
});

app.directive("reviews", function() {
  return {
    restrict: "E",
    templateUrl: "C:\\Users\\akshat.gupta\\Documents\\atlas-master\\mysite\\atlas\\templates\\comparison\\reviews.html"
  };
});

app.directive("specs", function() {
  return {
    restrict: "E",
    templateUrl: "C:\\Users\\akshat.gupta\\Documents\\atlas-master\\mysite\\atlas\\templates\\comparison\\specs.html"
  };
});

app.directive("productTabs", function() {
  return {
    restrict: "E",

    templateUrl: "C:\\Users\\akshat.gupta\\Documents\\atlas-master\\mysite\\atlas\\templates\\comparison\\product-tabs.html",
    controller: function() {
      this.tab = 1;

      this.isSet = function(checkTab) {
        return this.tab === checkTab;
      };

      this.setTab = function(activeTab) {
        this.tab = activeTab;
      };
    },
    controllerAs: "tab"
  };
});
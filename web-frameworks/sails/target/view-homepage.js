module.exports = {


  friendlyName: 'View homepage or redirect',


  description: 'Display or redirect to the appropriate homepage, depending on login status.',


  exits: {
    success: {
      viewTemplatePath: 'pages/homepage'
    }
  },


  fn: async function () {
    return {};
  }


};

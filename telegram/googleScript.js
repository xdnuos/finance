/**
 * This script is running on script.google.com
 *
 * receive data from client then write to spreadsheet
 *
 * sample data: '{"name":"Tiền bim bim", "amount":15000000 , "date": "11/9/2023"}'
 */
function doPost(e) {
  var data = JSON.parse(e.postData.contents);
  if (data.action == "add") {
    return add(e);
  }

  if (data.action == "delete_row") {
    return delete_row(e);
  }

  return ContentService.createTextOutput("Invalid action");
}

function add(e) {
  // TODO you should change the spreadsheetId here by your spreadsheetId --> copy from url --> https://docs.google.com/spreadsheets/d/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/edit#gid=0
  var spreadsheetId = "1FfZOET9rwsTFiSINmbacgC-XabNOt0XSS9v6kIyi8wA";

  var data = JSON.parse(e.postData.contents);

  // validate data here must have name, amount, date, type, source
  if (!data.name || !data.amount || !data.date) {
    return ContentService.createTextOutput("Missing required fields");
  }

  var [name, amount, date] = [data.name, data.amount, data.date];
  var sheetName = data.sheetName;

  // get sheet by name
  var sheet = SpreadsheetApp.openById(spreadsheetId).getSheetByName(sheetName);

  // scan for empty row in column A
  var range = sheet.getRange("A:A");
  var values = range.getValues();

  var row = 0;
  for (var i = 0; i < values.length; i++) {
    var rowValue = values[i][0];
    if (rowValue == "" || rowValue == null || rowValue == undefined) {
      row = i + 1;
      break;
    }
  }

  // create new row data
  var newRow = [name, amount, date];

  // write to spreadsheet
  sheet.getRange(row, 1, 1, newRow.length).setValues([newRow]);

  // copy format from row 1 to new row
  sheet
    .getRange(row, 1, 1, newRow.length)
    .copyFormatToRange(sheet, 1, newRow.length, row, row);

  // return response to client
  return ContentService.createTextOutput(
    `Add ${name} - ${Number(amount).toLocaleString()}đ ${date} at row ${row}`
  );
}

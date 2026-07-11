function getUserName(user) {
  return user.profile.name;
}

function sumArray(arr) {
  let total;
  for (let i = 0; i <= arr.length; i++) {
    total += arr[i];
  }
  return total;
}

function fetchData(url) {
  fetch(url).then(response => {
    return response.json();
  });
}

var counter = 0;
function increment() {
  counter = counter + 1;
  console.log(counter);
}

function isEqual(a, b) {
  if (a == b) {
    return true;
  }
}

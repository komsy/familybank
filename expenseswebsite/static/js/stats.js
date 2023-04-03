const renderChat = (data, labels)=>{

const ctx = document.getElementById('myChart');

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Expenses per Category',
        data: data,
        borderColor: '#36A2EB',
        backgroundColor: '#9BD0F5',
        borderWidth: 1
      }]
    },
    options: {
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });
};

const getChardata = () =>{
    fetch('/expense_category_summary').then((res)=>res.json()).then((results)=>{
        // console.log('results', results);
        const category_data = results.expense_category_data;
        const [labels,data]=[
            Object.keys(category_data),
            Object.values(category_data),
        ];
        renderChat(data, labels);
    });
};

document.onload = getChardata();
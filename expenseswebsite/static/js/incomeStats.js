const renderChat = (data, labels)=>{

    const ctx = document.getElementById('myChart');

      new Chart(ctx, {
        type: 'pie',
        data: {
          labels: labels,
          datasets: [{
            label: 'Incomes per Source',
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
        fetch('/income/income_source_summary').then((res)=>res.json()).then((results)=>{
            //console.log('results', results);
            const source_data = results.income_source_data;
            const [labels,data]=[
                Object.keys(source_data),
                Object.values(source_data),
            ];
            renderChat(data, labels);
        });
    };
    
    document.onload = getChardata();
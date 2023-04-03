const searchField = document.querySelector("#searchField");
const paginationContainer = document.querySelector(".pagination-container")

// Hide search output table by default
const appTable = document.querySelector(".app-table")
const tableOutput = document.querySelector(".table-output")
tableOutput.style.display = "none"
const tBody = document.querySelector(".table-body")
const noResults = document.querySelector(".no-results")

searchField.addEventListener("keyup", (e) => {
    const searchValue = e.target.value;

    if (searchValue.trim().length > 0) {
        paginationContainer.style.display = "none"
        tBody.innerHTML = "";
        fetch("/search-expenses",{
            body: JSON.stringify({ searchText: searchValue }),
            method: "POST",
        }).then((res)=>res.json())
          .then((data)=>{
            // console.log('data', data);
            appTable.style.display = "none"
            tableOutput.style.display = "block"

            // check if we get results
            if(data.length ===0 ){
                noResults.style.display = "block";
                tableOutput.style.display = "none";
            }else{
                noResults.style.display = "none";
                data.forEach((item)=>{ 
                    tBody.innerHTML += `
                    <tr>
                    <td>${ item.category }</td>
                    <td>${ item.description }</td>
                    <td>${ item.amount }</td>
                    <td>${ item.date }</td>
                    </tr>`;
                })
            }
        });
    }else{
        appTable.style.display = "block"
        paginationContainer.style.display = "block"
        tableOutput.style.display = "none"

    }
});
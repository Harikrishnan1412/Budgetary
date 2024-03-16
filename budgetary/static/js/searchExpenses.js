// Calling field value using id
SearchField = document.querySelector("#searchField");
tableOutput = document.querySelector(".table-output");
paginationContainer = document.querySelector(".pagination-control")
appTable = document.querySelector('.app-table');
tbody = document.querySelector(".table-body");
tableOutput.style.display = "none";

SearchField.addEventListener("keyup", (e)=>{
    const search_value = e.target.value;
    tbody.innerHTML = "";
    if(search_value.trim().length>0){
        fetch("/search-expenses",{
            body:JSON.stringify({searchText:search_value}),
            method:"POST",
        })
        .then((res)=>res.json())
        .then((data)=>{
            console.log("data",data);
            // Something in search table block old table display new table
            appTable.style.display = "none";
            tableOutput.style.display = "block";
            paginationContainer.style.display = "none";

            if(data.length === 0){
                tableOutput.innerHTML = "No result found";
            }
            else{
                data.forEach((item) =>{
                    tbody.innerHTML += `
                    <tr>
                    <td>${item.amount}</td>
                    <td>${item.category}</td>
                    <td>${item.description}</td>
                    <td>${item.date}</td>
                    </tr>
                    `
                });
            }
        })
    }
    else{
        // If nothing in search 
        // Display odl table
        tableOutput.style.display = "none";
        appTable.style.display = "block";
        paginationContainer.style.display = "block";
    }
})
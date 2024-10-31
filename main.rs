use ntex::web;
use reqwest;
use sailfish::TemplateSimple;
use serde_json::to_string_pretty;
use sqlite;
use std::collections::HashMap;


#[derive(TemplateSimple)]
#[template(path = "index.stpl")]
struct FilledTemplate {}


#[web::get("/")]
async fn index() -> impl web::Responder {
    // let output = handle_request("nice".to_string()).await.to_owned();
    let ctx = FilledTemplate {};
    return ntex::http::Response::Ok()
        .header("content-type", "text/html")
        .body(ctx.render_once().unwrap());
}

#[web::get("/next/{name}")]
async fn named(path: web::types::Path<String>) -> impl web::Responder {
    let name = path.into_inner();
    let output = handle_request(name).await.to_owned();
    return ntex::web::HttpResponse::Ok()
        .header("content-type", "application/json")
        .body(to_string_pretty(&output).unwrap());
}

async fn handle_request(name: String) -> Vec<HashMap<String, String>> {
    // creaete json request
    let mut map = HashMap::new();
    let mut padded_name = name.to_string();
    while padded_name.len() < 40 {
        padded_name.push(' ');
    }
    map.insert("item_id", padded_name);
    map.insert("amount_of_results", "150".to_string());
    let client = reqwest::Client::new();
    // send json request
    let search_results = client
        .post("http://localhost:8989/get_by_id")
        .json(&map)
        .send()
        .await
        .unwrap();
    let word_results: Vec<HashMap<String, String>> = search_results.json().await.unwrap();
    // prepare for sqlite3 searech
    let mut w: Vec<String> = Vec::<String>::new();
    let keep_word_indices = [0, 6, 61, 95, 116, 129, 137, 142, 145, 147, 148, 149];
    for item in 0..word_results.len() {
        if keep_word_indices.contains(&item) {
            w.push(word_results[item]["id"].trim_end().to_string());
        }
    }
    let connection =
        sqlite::open("/root/lang.db.sqlite3")
            .unwrap();
    connection.execute("PRAGMA synchronous = OFF");
    connection.execute("PRAGMA journal_mode = MEMORY");
    let sqlite_query = format!("select * from words where en_words in ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}');", w[0], w[1], w[2], w[3], w[4], w[5], w[6], w[7], w[8], w[9], w[10]);
    let mut output: Vec<HashMap<String, String>> = Vec::<HashMap<String, String>>::new();
    // do sqlite search
    connection
        .iterate(sqlite_query, |row| {
            let mut word_map: HashMap<String, String> = HashMap::new();
            for counter in 0..row.len() {
                let word = row[counter].1;
                match word {
                    Some(ok) => word_map.insert(row[counter].0.to_string(), ok.to_string()),
                    None => word_map.insert(row[counter].0.to_string(), "missing!".to_string()),
                };
            }
            output.push(word_map);
            true
        })
        .unwrap();
    //return words from sqlite chosen by similarity server
    return output;
}

#[ntex::main]
async fn main() -> std::io::Result<()> {
    web::HttpServer::new(|| web::App::new().service(index).service(named))
        .bind(("localhost", 8080))?
        .run()
        .await
}

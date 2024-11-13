# API DOCUMENT

## NODE

### Publish file
- __API__: `/api/files/publish`
- __Description__: Thông báo file muốn chia sẻ cho tracker biết
- __Body__:
```bash
{
    "name": string, // Tên file
    "size": number, // Kích thước file
    "hash_info": string, // Hash info của file
    "peer": { // Địa chỉ của peer, gồm address (IP) và port
        "address": string, 
        "port": string
    }
}
```
- __Response__
```bash
{
    "success": boolean,
    "message": string,
    "data": {
        "name": string,
        "size": number,
        "hash_info": string,
        "peer": {
            "address": string,
            "port": string
        },
        "_id": string
    }
}
```

### Fetch file
- __API__: `/api/files/fetch`
- __Description__: Lấy danh sách file đang được chia sẻ
- __Params__: `hash_info`
- __Response__:
```bash
{
    "success": boolean,
    "message": string,
    "data": [] // Nếu fetch có và không có params sẽ khác nhau
}
```
## TRACKER

### Discorver
- __API__: `/api/peers/discover`
- __Description__: Lấy danh sách tất cả các peer

## Create
- __API__: `/api/peers/create`
- __Description__: Thêm peer mới

### Ping
- __API__: `/api/peers/ping`
- __Descripiton__: Kiểm tra peer
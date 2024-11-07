import { Request, Response } from "express";
import { FileModel } from "../models/file.model";


export class FileController {

    async fetch(req: Request, res: Response): Promise<void> {
        try {
            const hash_info = req.query.hash_info;
            let files;
            if (hash_info) {
                const result = await FileModel.find({ hash_info: hash_info });
                let firstRes;
                if (result) firstRes = result[0];
                let peers: any[] = [];
                result.forEach((r) => {
                    peers.push(r.peer);
                });
                files = {
                    name: firstRes?.name,
                    size: firstRes?.size,
                    hash_info: firstRes?.hash_info,
                    peers: peers
                }

                res.status(200).json({
                    success: true,
                    message: `Fetch file by hash_info successfully`,
                    data: [files]
                });
            } else {
                files = await FileModel.find({});
                res.status(200).json({
                    success: true,
                    message: `Fetch all files successfully`,
                    data: files
                });
            }



        } catch (error: any) {
            res.status(500).json({
                success: false,
                message: error.message,
                data: []
            });
        }
    };

    async publish(req: Request, res: Response): Promise<void> {
        try {

            const isExist = await FileModel.findOne({
                'hash_info': req.body.hash_info,
                'peer.address': req.body.peer.address,
                'peer.port': String(req.body.peer.port)
            });

            if (isExist) {
                res.status(500).json({
                    success: true,
                    message: "File existed",
                    data: null
                });
                return;
            }

            const file = await FileModel.create(req.body);
            res.status(200).json({
                success: true,
                message: "Upload file sucessfully",
                data: file
            });
        } catch (error: any) {
            res.status(500).json({
                success: false,
                message: error.message,
                data: []
            });
        }
    }
}
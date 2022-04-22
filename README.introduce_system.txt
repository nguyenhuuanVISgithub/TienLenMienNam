- Tại mỗi lượt chơi, người chơi sẽ nhận được đầu vào là state bao gồm các keys sau:
	+ 'board': trạng thái bàn chơi hiện tại
		các thuộc tính được truy cập của Board:
			* name
			* show_cards: bài mà tất cả người chơi đã đánh ra
			* current_cards: bài hiện tại trên bàn cần chặt
			* set_of_cards: ('tên của bộ', điểm của bộ, 'tên người chơi đánh bộ đó')
	+ 'players': danh sách các người chơi
		các thuộc tính được truy cập của Player:
			* name
			* played_cards: bài mà người chơi đó đã đánh ra
	+ 'playing_id': danh sách id người chơi hiện tại trong vòng chơi (ai ko có id trong này
		tức là đã bỏ vòng)
	+ 'cur_player_id': id của người chơi lượt chơi hiện tại
	+ 'cur_player_cards': các lá bài của người chơi lượt chơi hiện tại

- Các thuộc tính của thẻ bài:
	+ name: tên thường sử dụng khi gọi lá bài
		Spade: Bích, Club: Nhép (Tép), Diamond: Rô, Heart: Cơ
		Jack: J, Queen: Q, King: K, Ace: Át
	+ stt: stt của thẻ bài trong bộ bài. stt càng cao thì giá trị của quân bài càng lớn
		một bộ bài gồm 52 lá bài với stt lần lượt từ 0 đến 51
		lá '3 Spade' có stt là 0 là lá yếu nhất
		lá '2 Heart' có stt là 51 là lá mạnh nhất
	+ card_type: chất của quân bài đó
		Spade: Bích, Club: Nhép (Tép), Diamond: Rô, Heart: Cơ